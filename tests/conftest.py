import pytest
from streamlit.testing.v1.element_tree import ButtonGroup

# Fix upstream Streamlit 1.41.1 AppTest bug where single-select ButtonGroup.indices
# iterates over character-by-character if self.value is a string, and select/unselect assumes list.
_orig_indices = ButtonGroup.indices.fget

def _fixed_indices(self):
    val = self.value
    if isinstance(val, str):
        val = [val]
    elif val is None:
        val = []
    return [self.options.index(self.format_func(v)) for v in val]

def _fixed_select(self, option):
    self.set_value([option])
    return self

def _fixed_unselect(self, option):
    self.set_value([])
    return self

ButtonGroup.indices = property(_fixed_indices)
ButtonGroup.select = _fixed_select
ButtonGroup.unselect = _fixed_unselect
