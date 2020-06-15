import asyncio
from enum import Enum
import random
import os

from pyppeteer import launcher
from pyppeteer.browser import Browser
from pyppeteer.connection import Connection

from bopbot.browser.exceptions import BrowserSetupError


def create_path(path):
    try:
        os.makedirs(path, exist_ok=True, mode=0o777)
    except Exception:
        raise


class SupportedOS(Enum):
    mac = "mac"
    linux = "linux"


def get_chrome_path(running_os: SupportedOS):
    if running_os == SupportedOS.mac:
        exe_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif running_os == SupportedOS.linux:
        exe_path = "/usr/bin/google-chrome"
    else:
        raise BrowserSetupError(f"running_os {running_os} must be of type SupportedOS enum")

    return exe_path


class BrowserWindow:
    def __init__(
        self,
        width=1200,
        height=800,
        use_size_buffer=True,
    ):
        """
        Parameters
        ==========
        width: Pixel width to render browser window
        height: Pixel height to render browser window
        use_size_buffer: If True, randomly subtracts/adds pixel value between (self.min_size, 250)
                         to window width & height
        """
        self.validate_window_sizes(width=width, height=height)
        self.width = width
        self.height = height
        if use_size_buffer:
            self.set_buffer()

    @property
    def min_size(self) -> int:
        return 50

    def validate_window_sizes(self, width, height):
        if self.min_size > width:
            raise BrowserSetupError(
                f"width size must be {self.min_size} or greater. Passed width: {width}"
            )
        elif self.min_size > height:
            raise BrowserSetupError(
                f"height size must be {self.min_size} or greater. Passed height: {height}"
            )
        else:
            return True

    def _random_buffer_size(self):
        return random.randint(self.min_size, 250)

    def _set_negative_buffer(self):
        buffer = self._random_buffer_size()
        self.width = random.randint(self.width - buffer, self.width)
        self.height = random.randint(self.height - buffer, self.height)

    def _set_possitive_buffer(self):
        buffer = self._random_buffer_size()
        self.width = random.randint(self.width, self.width + buffer)
        self.height = random.randint(self.height, self.height + buffer)

    def set_buffer(self):
        use_negative_buffer = random.random() > 0.5
        if use_negative_buffer:
            self._set_negative_buffer()
        else:
            self._set_possitive_buffer()

    @property
    def view_port(self) -> {}:
        return {"width": self.width, "height": self.height}

    def as_arg_option(self):
        return f"--window-size={self.width},{self.height+100}"


class BrowserConfig:
    def __init__(
        self,
        running_os: SupportedOS,
        browser_window: BrowserWindow,
        dev_mode=False,
        native_headless=False,
        xvfb_headless=False,
    ):
        """
        Parameters
        ==========
        running_os: OS we're executing the bopbot on
        browser_window: browser window dimensions
        dev_mode: if true, we open browser's JS developer console
        """
        self.running_os = running_os
        self.browser_window = browser_window
        self.exe_path = get_chrome_path(running_os=running_os)
        self.dev_mode = dev_mode
        self.native_headless = native_headless
        self.xvfb_headless = xvfb_headless
        self.validate_headless()
        self.browser_profile_path = "browserData"
        create_path(path=self.browser_profile_path)

    def validate_headless(self):
        """
        Checks if xvfb_headless headless is enabled. If enabled and running
        OS is not linux, we default headless mode to native_headless mode
        - xvfb_headless is only supported for linux OS
        """
        if self.xvfb_headless and self.running_os != SupportedOS.linux:
            self.native_headless = True
            self.xvfb_headless = False

    @property
    def slow_down(self) -> int:
        return random.randint(1, 3)

    def default_args(self) -> []:
        process_args = [
            '--cryptauth-http-host ""',
            "--disable-accelerated-2d-canvas",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-browser-side-navigation",
            "--disable-client-side-phishing-detection",
            "--disable-default-apps",
            "--disable-dev-shm-usage",
            "--disable-device-discovery-notifications",
            "--disable-extensions",
            "--disable-features=site-per-process",
            "--disable-hang-monitor",
            "--disable-java",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-setuid-sandbox",
            "--disable-sync",
            "--disable-translate",
            "--disable-web-security",
            "--disable-webgl",
            "--metrics-recording-only",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
            "--no-sandbox",
            "--remote-debugging-port",
            # Automation arguments
            "--password-store=basic",
            "--use-mock-keychain",
            "--disable-http2",
            # allow user agent override
            "--enable-features=NetworkService",
            self.browser_window.as_arg_option(),
        ]
        if self.dev_mode:
            process_args.append("--auto-open-devtools-for-tabs")

        return process_args

    def chrome_launch_options(self):
        process_args = self.default_args()
        return {
            "ignoreHTTPSErrors": True,
            "slowMo": self.slow_down,
            "userDataDir": self.browser_profile_path,
            "logLevel": "CRITICAL",
            "args": process_args,
            "ignoreDefaultArgs": [
                "--enable-automation",
                "--mute-audio",
                "--hide-scrollbars",
            ],
            "executablePath": self.exe_path,
            "defaultViewport": self.browser_window.view_port,
        }


class ChromeLauncher(launcher.Launcher):
    def __init__(
        self,
        chrome_config: BrowserConfig,
        loop=None,
    ):
        """
        Parameters
        ==========
        chrome_config: BrowserConfig
        loop: execution loop for chrome to use. If not set, launcher.Launcher creates one
        """
        options = chrome_config.chrome_launch_options()
        options["loop"] = loop
        super().__init__(options=options)
        # launcher.Launcher properties
        self.autoClose = False
        # custom properties for inheriting class
        self.executable_path = chrome_config.exe_path
        self.xvfb_headless = chrome_config.xvfb_headless
        self.native_headless = chrome_config.native_headless

    def _launch_cmd(self):
        if self.xvfb_headless:
            cmd = [
                "xvfb-run",
                "--auto-servernum",
                "-e",
                "/dev/stdout",
                self.executable_path
            ]
        elif self.native_headless:
            cmd = [
                self.executable_path,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--mute-audio"
            ]
        else:
            cmd = [self.executable_path]

        return cmd

    async def launch_chrome(self):
        self.chromeClosed = False
        self.connection = None
        self.proc = subprocess.Popen(
            self._launch_cmd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        # Signal handlers for exits used to be here
        connectionDelay = self.options.get("slowMo", 0)
        self.browserWSEndpoint = await self._get_ws_endpoint()
        self.connection = Connection(
            self.browserWSEndpoint, self._loop, connectionDelay
        )
        return await Browser.create(
            self.connection, self.options, self.proc, self.kill_chrome
        )

    def remove_xvfb_lock_file(self):
        lock_file_query = "/tmp/.X*-lock"
        lock_files_found = glob.glob(lock_file_query)
        for lock_file in lock_files_found:
            os.remove(lock_file)

    def kill_xvfb_process(self):
        process_name = "xvfb"
        existing_pids = psutil.pids()
        for pid in existing_pids:
            process = psutil.Process(pid)
            if process.name().lower() == process_name:
                process.kill()
                self.remove_xvfb_lock_file()
                break

    async def close_chrome(self):
        await self.killChrome()
        if self.xvfb_headless:
            self.kill_xvfb_process()
