import os
import random

from bopbot import BASE_DIR
from bopbot.jsinject.const import CHROME_VERSIONS


def get_random_chrome_version():
    version_numbers = []
    for releases in CHROME_VERSIONS.values():
        version_numbers.extend(releases)
    return random.choice(version_numbers)


def get_default_user_agent():
    mozzila = "Mozilla/5.0"
    running_os = "Windows NT 10.0; Win64; x64"
    webkit = "AppleWebKit/537.36 (KHTML, like Gecko)"
    chrome_version = f"Chrome/{get_random_chrome_version()} Safari/537.36"

    return f"{mozzila} ({running_os}) {webkit} {chrome_version}"


class JSLibs:
    def __init__(self):
        self._cache = {}

    def compose_resource_path(self, resource, lib_path="static"):
        if ".js" not in resource:
            resource = resource + ".js"

        if resource in self._cache.keys() and not force_load:
            return self._cache[resource]

        return os.path.join(BASE_DIR, lib_path, resource)

    def load_lib(self, resource, lib_path="static", force_load=False):
        if resource in self._cache:
            return self._cache[resource]

        resource_path = self.compose_resource_path(resource, lib_path)
        try:
            with open(resource_path, "r") as reader:
                self._cache[resource] = reader.read()

            return self._cache[resource]
        except FileNotFoundError as ex:
            error_message = "{}{}{}".format(
                "Loading pip package resource failure. We expected",
                f' [{os.path.join("<pip_lib_path>", lib_path, resource)}]',
                " yet what we got was [{}]".format(resource_path),
            )
            raise FileNotFoundError(error_message)
        except Exception:
            raise

    @property
    def override(self):
        return self.load_lib("override")

    @property
    def jquery(self):
        return self.load_lib("jquery-3.3.1.slim.min")


JS_LIBS = JSLibs()
