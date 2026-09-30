"""Notebook-oriented ML helpers."""

import numpy as np


def get_closest_matches(train, generated, n=12):
    closest = np.zeros(shape=(n, *generated.shape[1:]))
    closest_idx = np.zeros(shape=(n)).astype(int)
    closest_diff = np.zeros(shape=(n))

    for idx, g in enumerate(generated[0:n]):
        c_diff = 99999
        for sample_idx, sample in enumerate(train):
            diff = np.mean(np.abs(g - sample))
            if diff < c_diff:
                closest_idx[idx] = sample_idx
                closest[idx] = sample.copy()
                closest_diff[idx] = diff

                c_diff = diff

    return closest_idx, closest, closest_diff


def get_exact_matches_indices(train, generated):
    matches_idx = []
    for idx, sample in enumerate(train):
        for g in generated:
            if np.array_equal(g, sample):
                matches_idx.append(idx)
                break

    return np.array(matches_idx).astype(int)
