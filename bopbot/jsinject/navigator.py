import random

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
