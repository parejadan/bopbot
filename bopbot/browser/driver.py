import json
from user_agent import generate_navigator_js

from bopbot.browser.launcher import BrowserConfig, ChromeLauncher
from bopbot.jsinject.navigator import get_default_user_agent, JS_LIBS
from bopbot.browser.exceptions import PageError


class RawDriver:
    def __init__(
        self,
        chrome_config: BrowserConfig,
        user_agent: str=None,
        animation_timeout=5000,
        pageload_timeout=30000,
    ):
        """
        Parameters
        ==========
        chrome_config: BrowserConfig
        animation_timeout: miliseconds to wait for JS animation to render
        user_agent: user agent to spoof request header and navigator with
            - if not populated uses coded default with random chrome version
        pageload_timeout: amount of time we're willing to wait for page to load
        """
        self.chrome_config = chrome_config
        self.user_agent = user_agent if user_agent else get_default_user_agent()
        self.animation_timeout = animation_timeout
        self.pageload_timeout = pageload_timeout

    @property
    def page(self):
        return self.page_manager.page

    @property
    def loop(self):
        return self.launcher.loop

    async def get_new_browser(self):
        self.launcher = ChromeLauncher(chrome_config=self.chrome_config)
        self.browser = await self.launcher.launch_chrome()
        self.page_manager = PageManager(
            loop=self.loop,
            browser=self.browser,
            viewport=self.browser_config.browser_window.view_port,
            navigator_defaults=self.user_agent,
            timeout=self.pageload_timeout,
        )
        await self.page_manager.set_single_page()
        return self.browser

    async def goto(self, url):
        """
        Navigate to address
        """
        await self.page_manager.goto(url)


class PageManager:
    def __init__(self, loop, browser, viewport, user_agent, timeout):
        self.loop = loop
        self.browser = browser
        self.page = None
        self.os = ("win", "mac", "linux")
        self.viewport = viewport
        self.navigator_defaults = {
            "userAgent": user_agent,
            "os": self.os,
            "browser": "chrome",
            "mediaDevices": False,
            "webkitGetUserMedia": False,
            "mozGetUserMedia": False,
            "getUserMedia": False,
            "webkitRTCPeerConnection": False,
            "webdriver": False,
        }
        self.navigator_config = {}
        self.timeout = timeout

    @property
    def user_agent(self):
        return self.navigator_config.get(
            "userAgent", self.navigator_defaults.get("userAgent")
        )

    async def sync_request_agent(self):
        if self.user_agent:
            await self.page.setExtraHTTPHeaders(headers={"User-Agent": user_agent})

    async def resync_navigator(self, hard=False, use_custom_js=False):
        dump = json.dumps(self.navigator_config)
        _ = f"const _navigator = {dump};"

        injection = "{\n%s\n%s\n%s}" % (JS_LIBS.jquery, _, JS_LIBS.override)
        await self.page.evaluateOnNewDocument(f"() => {injection}")

        if hard:
            await self.page.setUserAgent(self.user_agent)
            await self.sync_request_agent()

    async def cloak_navigator(self):
        """
        Emulate another browser's navigator properties
        and set webdriver false, inject jQuery.
        """
        self.navigator_config = generate_navigator_js(os=self.os, navigator=("chrome"))
        self.navigator_config.update(self.navigator_defaults)
        await self.resync_navigator()

    async def goto(self, url, regenerate_navigator=False):
        if not self.navigator_config or regenerate_navigator:
            await self.cloak_navigator()
        await self.page.setUserAgent(self.user_agent)
        try:
            await self.loop.create_task(
                self.page.goto(url, timeout=self.timeout, waitUntil="domcontentloaded")
            )
        except asyncio.TimeoutError:
            raise PageError(f"Timeout loading {url}")
        except Exception as ex:
            raise PageError(f"While loading [{url}] encountered error{ex}")
