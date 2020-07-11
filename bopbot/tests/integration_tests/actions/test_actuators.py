import os
import pytest
from uuid import uuid4

from bopbot.actions.actuators import BaseAction
from bopbot.browser.driver import RawDriver
from bopbot.browser.launcher import BrowserConfig, BrowserWindow, SupportedOS
from bopbot.dom.elements import LabeledSelector


SANDBOX_ENDPOINT = "http://localhost:8080/"


def get_default_bot(headless_mode=True):
    chrome_config = BrowserConfig(
        browser_window=BrowserWindow(), xvfb_headless=headless_mode
    )
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
    async def test_selector_exists_even_if_hidden(self, bot):
        hidden_item = LabeledSelector(
            label="hidden_item",
            dom_hierarchy=["#app", "div", "ul:nth-child(6)", "li:nth-child(6)"],
        )
        assert await bot.selector_visible(elem=hidden_item) is False
        assert await bot.selector_exists(elem=hidden_item) is True

    @pytest.mark.asyncio
    @sandbox_exec
    async def test_type_and_clear_input(self, bot):
        random_input = LabeledSelector(
            label="random_input", dom_hierarchy=["#app", "div", "input[type=text]"],
        )
        input_message = "hello world input type"
        await bot.type(elem=random_input, text=input_message)
        assert await bot.query(elem=random_input, attr="value") == input_message
        await bot.clear(elem=random_input)
        assert await bot.query(elem=random_input, attr="value") == ""

    @pytest.mark.asyncio
    @sandbox_exec
    async def test_select_input(self, bot):
        random_dropdown = LabeledSelector(
            label="random_dropdown", dom_hierarchy=["#app", "div", "select"]
        )
        selected_option = "audi"
        await bot.select(elem=random_dropdown, text=selected_option)
        assert await bot.query(elem=random_dropdown, attr="value") == selected_option

    @pytest.mark.asyncio
    @sandbox_exec
    async def test_click_hide_show(self, bot):
        hide_show_button = LabeledSelector(
            label="hide_show_button", dom_hierarchy=[".hello", "button:nth-child(9)"]
        )
        random_input = LabeledSelector(
            label="random_input", dom_hierarchy=["#app", "div", "input[type=text]"],
        )
        assert await bot.selector_visible(elem=random_input) is True
        await bot.click(elem=hide_show_button)
        assert await bot.selector_exists(elem=random_input) is False
        await bot.click(elem=hide_show_button)
        assert await bot.selector_visible(elem=random_input) is True

    @pytest.mark.asyncio
    @sandbox_exec
    async def test_screenshot(self, bot):
        async def screenshot_mock(options):
            await bot.sleep_for(seconds=1)
            assert os.getcwd() in options["path"]

        bot.driver.page.screenshot = screenshot_mock
        await bot.screenshot()
