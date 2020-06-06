from enum import Enum
import random

from bopbot.browser.exceptions import BrowserSetupError


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
    def min_size(self):
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
    def view_port(self):
        return {"width": self.width, "height": self.height}


class BrowserConfig:
    def __init__(
        self,
        running_os: SupportedOS,
        page_load_timeout=30000,
        animation_timeout=5000,
        debug_mode=False,
        native_headless=False,
        xvfb_headless=False,
    ):
        """
        Parameters
        ==========
        running_os: OS we're executing the bopbot on
        page_load_timeout: miliseconds to wait for browser to load page
        animation_timeout: miliseconds to wait for JS animation to render
        debug_mode: If true, we open browser's JS debug console
        """
        self.running_os = running_os
        self.exe_path = get_chrome_path(running_os=running_os)
        self.page_load_timeout = page_load_timeout
        self.animation_timeout = animation_timeout
        self.native_headless = native_headless
        self.xvfb_headless = xvfb_headless
        self.validate_headless()
        self.browser_profile_path = "browserData"

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
    def slow_down(self):
        return random.randint(1, 3)
