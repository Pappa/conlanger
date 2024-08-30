import pytest
from conlanger.tools import SyllableStructure


@pytest.mark.parametrize(
    "weirdness, structure",
    [(0.1, "(C)V(C)"), (0.5, "(C)(G)V(C)"), (1.0, "(C)(C)V(C)(C)(C)")],
)
def test_SyllableStructure(weirdness, structure):
    ss = SyllableStructure(seed=0)
    assert ss.pick(weirdness=weirdness) == structure
