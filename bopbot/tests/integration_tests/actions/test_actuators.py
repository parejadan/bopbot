import pytest

from bopbot.actions.actuators import BaseAction
from bopbot.browser.driver import RawDriver
from bopbot.browser.launcher import BrowserConfig, BrowserWindow, SupportedOS
from bopbot.dom.elements import LabeledSelector


SANDBOX_ENDPOINT = "http://localhost:8080/"


def get_default_bot():
    chrome_config = BrowserConfig(browser_window=BrowserWindow(), xvfb_headless=True)
    chrome_driver = RawDriver(chrome_config=chrome_config)
    return BaseAction(driver=chrome_driver)


class TestBaseAction:
    @pytest.mark.asyncio
    async def test_clean_launch_and_close(self):
        title_selector = LabeledSelector(label="welcome", dom_hierarchy=["#app", "div", "h1"])
        bot = get_default_bot()
        await bot.driver.get_new_browser()
        await bot.driver.goto(url=SANDBOX_ENDPOINT)
        assert await bot.selector_exists(elem=title_selector) is True
        await bot.driver.close()
