from bopbot.jsinject.navigator import JS_LIBS, get_default_user_agent


class TestJSLibs:
    def test_successfully_load_required(self):
        JS_LIBS.clean()
        assert "override" not in JS_LIBS._cache
        assert JS_LIBS.override != None
        assert "override" in JS_LIBS._cache
        assert JS_LIBS.jquery != None


class TestGetDefaultUserAgent:
    def test_chrome_version_randomized(self):
        user_agent = get_default_user_agent()
        assert user_agent is not None
        assert user_agent != get_default_user_agent()
