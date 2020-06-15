import pytest
from mock import patch, Mock

from bopbot.browser.launcher import (
    SupportedOS,
    get_chrome_path,
    BrowserWindow,
    BrowserConfig,
    ChromeLauncher,
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
            width=start_width, height=start_height, use_size_buffer=False,
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
        browser_config = BrowserConfig(
            running_os=SupportedOS.mac,
            browser_window=BrowserWindow(),
            xvfb_headless=True,
        )
        assert browser_config.xvfb_headless == False
        assert browser_config.native_headless == True

    def test_window_flag_option(self):
        window = BrowserWindow()
        config = BrowserConfig(running_os=SupportedOS.linux, browser_window=window)
        assert window.as_arg_option() in config.default_args()

    def test_debug_flag_option(self):
        config = BrowserConfig(
            running_os=SupportedOS.linux, browser_window=BrowserWindow(), dev_mode=True,
        )
        assert "--auto-open-devtools-for-tabs" in config.default_args()

    def test_creates_browser_data_path(self):
        create_pat_mock = Mock()
        with patch("bopbot.browser.launcher.create_path", create_pat_mock):
            config = BrowserConfig(
                running_os=SupportedOS.linux,
                browser_window=BrowserWindow,
                dev_mode=True,
            )
        create_pat_mock.assert_called_with(path=config.browser_profile_path)

    def test_chrome_launch_options_defaults(self):
        window = BrowserWindow()
        config = BrowserConfig(
            running_os=SupportedOS.linux, browser_window=window, dev_mode=True
        )
        chrome_launch_options = config.chrome_launch_options()
        assert chrome_launch_options["ignoreHTTPSErrors"] == True
        assert chrome_launch_options["userDataDir"] == config.browser_profile_path
        assert chrome_launch_options["ignoreDefaultArgs"] == [
            "--enable-automation",
            "--mute-audio",
            "--hide-scrollbars",
        ]
        assert "executablePath" in chrome_launch_options
        assert chrome_launch_options["defaultViewport"] == window.view_port


class TestChromeLauncher:
    def test_xvfb_launch_cmd(self):
        browser_config = BrowserConfig(
            running_os=SupportedOS.linux,
            browser_window=BrowserWindow(),
            xvfb_headless=True,
        )
        launcher = ChromeLauncher(chrome_config=browser_config)
        launch_cmd = launcher._launch_cmd()

        assert "xvfb-run" in launch_cmd
        assert "--headless" not in launch_cmd

    def test_native_headless_launch_cmd(self):
        browser_config = BrowserConfig(
            running_os=SupportedOS.mac,
            browser_window=BrowserWindow(),
            native_headless=True,
        )
        launcher = ChromeLauncher(chrome_config=browser_config)
        launch_cmd = launcher._launch_cmd()

        assert "xvfb-run" not in launch_cmd
        assert "--headless" in launch_cmd

    def test_options_sync_chrome_config(self):
        browser_config = BrowserConfig(
            running_os=SupportedOS.mac,
            browser_window=BrowserWindow(),
            native_headless=True,
        )
        launcher = ChromeLauncher(chrome_config=browser_config)
        expected = browser_config.chrome_launch_options()
        assert launcher.chromeExecutable == browser_config.exe_path
        assert launcher.ignoreHTTPSErrors == expected["ignoreHTTPSErrors"]
        assert (
            f"--user-data-dir={browser_config.browser_profile_path}"
            in launcher.chromeArguments
        )
        # verify we're omiting the default arguments
        for ignore_arg in expected["ignoreDefaultArgs"]:
            assert ignore_arg not in launcher.chromeArguments
        # verify the needed arguments are present
        for required_arg in expected["args"]:
            assert required_arg in launcher.chromeArguments
