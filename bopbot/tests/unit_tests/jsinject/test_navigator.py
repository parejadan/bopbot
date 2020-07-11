from bopbot.jsinject.navigator import get_default_user_agent


class TestGetDefaultUserAgent:
    def test_chrome_version_randomized(self):
        user_agent = get_default_user_agent()
        assert user_agent is not None
        assert user_agent != get_default_user_agent()
