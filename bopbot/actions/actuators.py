import os
import asyncio
from uuid import uuid4

from pyppeteer.errors import TimeoutError
from pyppeteer.frame_manager import Frame
from pyppeteer.element_handle import ElementHandle

from bopbot.dom.elements import LabeledSelector
from bopbot.browser.driver import RawDriver
from bopbot.actions.exceptions import ElementNotFoundError
from bopbot.browser.launcher import BrowserConfig, BrowserWindow


class BaseAction:
    def __init__(self, driver: RawDriver):
        self.driver = driver

    def wait_for_element(self, elem: LabeledSelector, as_visible=True):
        """
        For a given selector we run a coroutine to wait for it durating a
        self.driver.animation_timeout period.
        - Best for waiting for elements to render during navigation or JS annimation

        Parameters
        ==========
        elem: selector to wait for
        as_visible: If True, we expect the element to be visible. If not visible
                    the coroutine fails even if selector exisits.
                    - If False we just wait for the selector to exists (no visibility)
        """
        try:
            self.driver.page.waitForSelector(
                selector=elem.to_str(),
                timeout=self.driver.animation_timeout,
                options={"visible": as_visible},
            )
        except TimeoutError:
            error_msg = "can not find element [{}] {}".format(
                elem.label, "visible" if as_visible else "even as not visible"
            )
            raise ElementNotFoundError(error_msg)

    async def query_frame(self, frame: Frame, elem: LabeledSelector, attr="innerText"):
        """
        Core function for self.query(...), but we do not default the query frame to
        self.driver.page

        Parameters
        ==========
        frame: iframe or web page to evaluate selector's query against
        elem: selector to query with
        attr: str to append to "document.querySelector(<selector>)."

        Returns
        =======
        Whatever the query evaluation results to
        """
        return await frame.evaluate(f"{elem.to_query()}.{attr}")

    async def query(self, elem: LabeledSelector, attr="innerText"):
        """
        For a given element we query properties of the dom object. For example:
        document.querySelector(<selector>).innerText

        We can also extend the querying to do boolean evaluations such as:
        document.querySelector(<selector>).style.display != "none"

        By default we query the self.driver.page

        Parameters
        ==========
        elem: selector to query with
        attr: str to append to "document.querySelector(<selector>)."

        Returns
        =======
        Whatever the query evaluation results to
        """
        return await self.query_frame(frame=self.driver.page, elem=elem, attr=attr)

    async def selector_exists_in_frame(self, frame: Frame, elem: LabeledSelector):
        """
        Core function for self.selector_exists(..) but we do not default frame to
        self.driver.page

        Parameters
        ==========
        frame: iframe or web page to evaluate selector's query against
        elem: selector to check if it exists in frame

        Returns
        =======
        True if selector exists in page otherwise False
        """
        try:
            return await frame.evaluate(f"{elem.to_query()} !== null")
        except Exception:
            return False

    async def selector_exists(self, elem: LabeledSelector):
        """
        For a given element we query self.driver.page to check if it exists or not
        - NOTE: does not wait for selector to render. If you want a wait routine
                use self.wait_for_element(..) instead.

        Parameters
        ==========
        elem: selector to check if it exists in self.driver.page

        Returns
        =======
        True if selector exists in page otherwise False
        """
        return await self.selector_exists_in_frame(frame=self.driver.page, elem=elem)

    async def click(self, elem: LabeledSelector, as_visible=True):
        self.wait_for_element(elem=elem, as_visible=as_visible)
        await self.driver.page.click(selector=elem.to_str())

    async def click_element_handle(self, elem: ElementHandle):
        await elem.click()

    async def selector_visible_in_frame(self, frame: Frame, elem: LabeledSelector):
        return await self.query_frame(
            frame=frame, elem=elem, attr="style.display != 'none'"
        )

    async def selector_visible(self, elem: LabeledSelector):
        return await self.selector_visible_in_frame(frame=self.driver.page, elem=elem)

    async def type(self, elem: LabeledSelector, text: str, delay=15):
        self.wait_for_element(elem=elem, as_visible=True)
        await self.driver.page.type(
            selector=elem.to_str(), text=text, options={"delay": delay}
        )

    async def select(self, elem: LabeledSelector, text: str):
        self.wait_for_element(elem=elem, as_visible=True)
        await self.driver.page.select(elem.to_str(), text)

    async def sleep_for(self, seconds=2):
        await asyncio.sleep(seconds)

    async def wait_for_navigation(self):
        await self.driver.page.waitForNavigation()

    async def clear(self, elem: LabeledSelector):
        await self.query(elem=elem, attr="value = ''")

    async def screenshot(self, filename: str = None):
        if not filename:
            filename = f"{uuid4()}"
        ouput_path = os.path.join(os.getcwd(), f"{filename}-capture.png")
        await self.driver.page.screenshot(options={"path": ouput_path})


def get_default_bot(headless_mode=True):
    chrome_config = BrowserConfig(
        browser_window=BrowserWindow(), xvfb_headless=headless_mode
    )
    chrome_driver = RawDriver(chrome_config=chrome_config)
    return BaseAction(driver=chrome_driver)
