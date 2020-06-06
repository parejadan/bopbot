import pytest

from bopbot.dom.elements import BaseSelector
from bopbot.dom.exceptions import SelectorError


class TestBaseSelector:
    def test_pop_syncs_to_str(self):
        selector = BaseSelector(dom_hierarchy=["body", "div", "div", "button"])
        initial_path = selector.to_str()
        selector.pop()
        assert initial_path != selector.to_str()
        assert selector.to_str() == selector._str

    def test_hierarchy_must_be_populated(self):
        selector = BaseSelector(dom_hierarchy=[])
        with pytest.raises(SelectorError):
            selector.to_str()

        selector.set_hierarchy(dom_hierarchy=1)
        with pytest.raises(SelectorError):
            selector.to_query()
