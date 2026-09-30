"""Notebook-oriented ML display helpers."""

import matplotlib.pyplot as plt


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
        raise ValueError("Not enough titles")

    cnt = 0
    for i in range(r):
        for j in range(c):
            if titles is not None and titles[cnt] is not None:
                axs[i, j].set_title(titles[cnt][0:18], fontsize=12)
            axs[i, j].imshow(images[cnt], cmap=cmap)
            axs[i, j].axis("off")
            cnt += 1

    plt.show()
