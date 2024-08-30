import pytest
import numpy as np
from conlanger.utils import get_closest_matches, get_exact_matches_indices, display_rows


@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([[1, 2, 3], [4, 5, 6]], [[1, 2, 3], [4, 5, 6]], [0, 1]),
        ([[1, 2, 3], [4, 5, 6]], [[1, 2, 3], [4, 5, 2]], [0]),
        ([[1, 2, 3], [4, 5, 6]], [[1, 2, 5], [4, 5, 2]], []),
    ],
)
def test_get_exact_matches_indices(x, y, expected):
    matches = get_exact_matches_indices(np.array(x), np.array(y))
    assert np.array_equal(matches, np.array(expected))
