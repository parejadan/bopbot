import pytest

from bopbot.browser.driver import (
    SupportedOS,
    get_chrome_path,
    BrowserWindow,
    BrowserConfig,
)
from bopbot.browser.exceptions import BrowserSetupError


class TestSupportedOS:
    def test_has_all_defined_paths(self):
        for support_option in SupportedOS._member_names_:
            enum_option = getattr(SupportedOS, support_option)
            assert get_chrome_path(running_os=enum_option) != ""

    def test_get_chrome_path_rases_browser_setup_error(self):
        with pytest.raises(BrowserSetupError):
            get_chrome_path(running_os="win")


class TestBrowserWindow:
    def test_set_negative_buffer(self):
        start_width, start_height = 100, 100
        browser_window = BrowserWindow(
            width=start_width,
            height=start_height,
            use_size_buffer=False,
        )
        browser_window._set_negative_buffer()
        assert start_width > browser_window.width
        assert start_height > browser_window.height

    def test_set_possitive_buffer(self):
        start_width, start_height = 100, 100
        browser_window = BrowserWindow(use_size_buffer=False)
        browser_window._set_possitive_buffer()
        assert start_width < browser_window.width
        assert start_height < browser_window.height

    def test_validates_window_size(self):
        with pytest.raises(BrowserSetupError):
            BrowserWindow(width=10, height=100)
        with pytest.raises(BrowserSetupError):
                BrowserWindow(width=100, height=10)
        with pytest.raises(BrowserSetupError):
                BrowserWindow(width=10, height=10)


class TestBrowserConfig:
    def test_validate_headless(self):
        browser_config = BrowserConfig(running_os=SupportedOS.mac, xvfb_headless=True)
        assert browser_config.xvfb_headless == False
        assert browser_config.native_headless == True
