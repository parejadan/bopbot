from bopbot.dom.exceptions import SelectorError


def validate_dom_hierarchy(dom_hierarchy: [str]):
    """
    If passed dom_hierarchy is a populated list returns true, otherwise
    raises SelectorError
    """
    if not isinstance(dom_hierarchy, list) or not dom_hierarchy:
        raise SelectorError(
            f"passed dom_hierarchy [{dom_hierarchy}] is not a populated list"
        )

    return True


class BaseSelector:
    """
    Resource for defining a dom's CSS selector path in list form.
    To use for js quering we define a dom_connector that's used by
    flatten_hierarchy(..) to produce str like:
    - '#main > div > ol > li > a'

    We define the js query format as 'document.querySelector("{}")'
    to assure across browser compatibility.
    """
    dom_connector = ">"

    def __init__(self, dom_hierarchy: [str]):
        """
        @dom_hierarchy: list of HTML/DOM tags in order representing path to selector.
                    Last element assumed to be target dom element.
        """
        self._dom_hierarchy = dom_hierarchy
        self.query_format = "document.querySelector(\"{}\")"
        self._str = None

    @classmethod
    def flatten_hierarchy(cls, dom_hierarchy):
        validate_dom_hierarchy(dom_hierarchy=dom_hierarchy)
        return f" {cls.dom_connector} ".join(dom_hierarchy)

    def to_str(self, dom_hierarchy: [str] = None) -> str:
        if dom_hierarchy:
            parsed = BaseSelector.flatten_hierarchy(dom_hierarchy=dom_hierarchy)
        elif not self._str:
            parsed = self._str = BaseSelector.flatten_hierarchy(
                dom_hierarchy=self._dom_hierarchy
            )
        else:
            parsed = self._str

        return parsed

    def to_query(self, dom_hierarchy: [str] = None) -> str:
        if dom_hierarchy:
            query_str = self.query_format.format(self.to_str(dom_hierarchy=dom_hierarchy))
        else:
            query_str = self.query_format.format(self.to_str())

        return query_str

    def pop(self):
        self._dom_hierarchy.pop()
        self._str = None

    def set_hierarchy(self, dom_hierarchy: [str]):
        self._dom_hierarchy = dom_hierarchy
        self._str = None

    @property
    def is_empty(self):
        return len(self._dom_hierarchy) == 0
