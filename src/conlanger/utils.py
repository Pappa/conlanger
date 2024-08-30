import matplotlib.pyplot as plt
import numpy as np


def display_rows(
    images,
    titles=None,
    size=(12, 12),
    r=3,
    c=6,
    cmap="gray_r",
):
    """
    Displays n random images from each one of the supplied arrays.
    """
    if images.max() > 1.0:
        images = images / 255.0
    elif images.min() < 0.0:
        images = (images + 1.0) / 2.0

    _, axs = plt.subplots(r, c, figsize=size)

    if titles is not None and len(titles) < r * c:
        raise

    cnt = 0
    for i in range(r):
        for j in range(c):
            if titles is not None and titles[cnt] is not None:
                axs[i, j].set_title(titles[cnt][0:18], fontsize=12)
            axs[i, j].imshow(images[cnt], cmap=cmap)
            axs[i, j].axis("off")
            cnt += 1

    plt.show()


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
