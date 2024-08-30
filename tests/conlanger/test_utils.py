import pytest
import numpy as np
from conlanger.utils import get_closest_matches, get_exact_matches_indices, display_rows


@pytest.mark.parametrize(
    "x, y, expected_idx, expected, expected_diff",
    [
        ([[1, 2, 3], [4, 5, 6]], [[1, 2, 6], [40, 50, 100]], [0], [[1, 2, 3]], [1]),
        ([[1, 2, 3], [4, 5, 6]], [[4, 8, 12], [4, 5, 6]], [1], [[4, 5, 6]], [3]),
    ],
)
def test_get_closest_matches(x, y, expected_idx, expected, expected_diff):
    closest_idx, closest, closest_diff = get_closest_matches(
        np.array(x), np.array(y), n=1
    )
    assert np.array_equal(closest_idx, np.array(expected_idx))
    assert np.array_equal(closest, np.array(expected))
    assert np.array_equal(closest_diff, np.array(expected_diff))


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
