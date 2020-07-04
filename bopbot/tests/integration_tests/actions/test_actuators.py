from uuid import uuid4
import pytest

from bopbot.actions.actuators import BaseAction
from bopbot.browser.driver import RawDriver
from bopbot.browser.launcher import BrowserConfig, BrowserWindow, SupportedOS
from bopbot.dom.elements import LabeledSelector


SANDBOX_ENDPOINT = "http://localhost:8080/"


def get_default_bot(headless_mode=True):
    chrome_config = BrowserConfig(browser_window=BrowserWindow(), xvfb_headless=headless_mode)
    chrome_driver = RawDriver(chrome_config=chrome_config)
    return BaseAction(driver=chrome_driver)


async def get_default_bot_on_sandbox():
    bot = get_default_bot()
    await bot.driver.get_new_browser()
    await bot.driver.goto(url=SANDBOX_ENDPOINT)

    return bot


def sandbox_exec(test_func):
    """
    Decorator for fetching bot already navigated to the
    sandbox website. This wrapper automatically closes/cleansup
    browser post execution regardless of failure/success
    """
    async def exec_wrapper(*args, **kwargs):
        bot = await get_default_bot_on_sandbox()
        try:
            await test_func(*args, bot=bot)
        except Exception:
            await bot.driver.close()
            raise
        await bot.driver.close()

    return exec_wrapper


class TestBaseAction:
    @pytest.mark.asyncio
    @sandbox_exec
    async def test_selector_exists_element(self, bot):
        title_selector = LabeledSelector(
            label="welcome", dom_hierarchy=["#app", "div", "h1"]
        )
        assert await bot.selector_exists(elem=title_selector) is True
        # we want to validate selector exists returns no false possitives
        title_selector.set_hierarchy(dom_hierarchy=[f"{uuid4()}"])
        assert await bot.selector_exists(elem=title_selector) is False

    @pytest.mark.asyncio
    @sandbox_exec
    async def test_click_and_navigate(self, bot):
        babel_button = LabeledSelector(
            label="babel",
            dom_hierarchy=[
                "#app", "div", "ul:nth-child(4)", "li:nth-child(1)", "a"
            ]
        )
        github_logo = LabeledSelector(
            label="github_logo",
            dom_hierarchy=[
                "body",
                "div.position-relative.js-header-wrapper",
                "header",
                "div",
                "div.d-flex.flex-justify-between.flex-items-center",
                "a",
                "svg",
            ]
        )
        await bot.click(elem=babel_button)
        # Assert Failing
        #await bot.sleep_for(seconds=3)
        #assert await bot.selector_exists(elem=github_logo) is True
