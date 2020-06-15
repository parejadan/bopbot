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


def validate_label_name(label):
    if not isinstance(label, str) or not label.replace("_", "").isalpha():
        raise SelectorError(
            f"label [{label}] must be str and only have alpha chars after label.replace('_', '')"
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
        self.query_format = 'document.querySelector("{}")'
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
            query_str = self.query_format.format(
                self.to_str(dom_hierarchy=dom_hierarchy)
            )
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


class LabeledSelector(BaseSelector):
    """
    Resource for defining dom paths with a human readable label describing
    the dom object
    """

    def __init__(self, label: str, dom_hierarchy: [str]):
        """
        Parameters
        ==========
        label: Human readable name representation for dom object.
               Label must be str and only have alphabetical chars after label.replace('_', '').
        dom_hierarchy: list of HTML/DOM tags in order representing path to selector.
                       Last element assumed to be target dom element.
        """
        validate_label_name(label=label)
        super().__init__(dom_hierarchy=dom_hierarchy)
        self.label = label


def flatten_selector_hierarchy(selector_hierarchy: []) -> []:
    """
    For a given list of items we unpack them to an extended
    list of objects that can be manipulated by BaseSelector.flatten_hierarchy(..)

    Parameters
    ==========
    selector_hierarchy: [
        BaseSelector,
        LabeledSelector,
        [str],
        str,
    ]

    Returns
    =======
    list items where validate_dom_hierarchy(...) will evaluate true against
    """
    flattened_hierarchy = []
    for item in selector_hierarchy:
        if isinstance(item, BaseSelector):
            flattened_hierarchy.extend(item._dom_hierarchy)
        elif isinstance(item, list):
            flattened_hierarchy.extend(item)
        else:
            flattened_hierarchy.append(item)
    validate_dom_hierarchy(dom_hierarchy=flattened_hierarchy)

    return flattened_hierarchy


def create_labeled_selector(label, selector_hierarchy: []) -> LabeledSelector:
    return LabeledSelector(
        label=label,
        dom_hierarchy=flatten_selector_hierarchy(selector_hierarchy=selector_hierarchy),
    )


def add_selector_to(obj, label: str, selector_hierarchy: []):
    """
    for a given object we create a DOMSelector instance with the specified label
    and hierarchy, then add obj an attribute named with the passed label value

    @obj: object we want to add this selector attribute to
    @label: camelcase string describing the object the passed dom path hierarchy points to
    @selector_hierarchy: DOM path that points to selector label describes
    """
    selector = create_labeled_selector(
        label=label, selector_hierarchy=selector_hierarchy
    )
    setattr(obj, label, selector)
