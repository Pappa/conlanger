import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np



def sample_batch(dataset):
    batch = dataset.take(1).get_single_element()
    if isinstance(batch, tuple):
        batch = batch[0]
    return batch.numpy()


def display(
    images, n=10, size=(20, 3), cmap="gray_r", as_type="float32", save_to=None
):
    """
    Displays n random images from each one of the supplied arrays.
    """
    if images.max() > 1.0:
        images = images / 255.0
    elif images.min() < 0.0:
        images = (images + 1.0) / 2.0

    plt.figure(figsize=size)
    for i in range(n):
        _ = plt.subplot(1, n, i + 1)
        plt.imshow(images[i].astype(as_type), cmap=cmap)
        plt.axis("off")

    if save_to:
        plt.savefig(save_to)
        print(f"\nSaved to {save_to}")

    plt.show()



def display_rows(
    images, titles=None, size=(12, 12), r=3, c=6, cmap="gray_r", as_type="float32", save_to=None
):
    """
    Displays n random images from each one of the supplied arrays.
    """
    if images.max() > 1.0:
        images = images / 255.0
    elif images.min() < 0.0:
        images = (images + 1.0) / 2.0

    fig, axs = plt.subplots(r, c, figsize=size)

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
    
def normalize_image_data(img):
    """
    Normalize and reshape the images
    """
    img = (tf.cast(img, "float32") - 127.5) / 127.5
    return img

def denormalize_image_data(img):
    return img * 255

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

def get_exact_matches(train, generated):
    matches_idx = []
    for idx, sample in enumerate(train):
        for g in generated:
            if np.array_equal(g, sample):
                matches_idx.append(idx)
                break
        
    return np.array(matches_idx).astype(int)