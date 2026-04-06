import numpy as np
from cellpose import models, core, io, plot
from pathlib import Path
from tqdm import trange
import matplotlib.pyplot as plt

io.logger_setup()  # run this to get printing of progress

# Check if colab notebook instance has GPU access
if core.use_gpu() == False:
    raise ImportError("No GPU access, change your runtime")

model = models.CellposeModel(gpu=True)

"""### Download example images"""

import numpy as np
import matplotlib.pyplot as plt
from cellpose import utils, io

# download example 2D images from website
url = "http://www.cellpose.org/static/data/imgs_cyto3.npz"
filename = "imgs_cyto3.npz"
utils.download_url_to_file(url, filename)

# download 3D tiff
url = "http://www.cellpose.org/static/data/rgb_3D.tif"
utils.download_url_to_file(url, "rgb_3D.tif")

dat = np.load(filename, allow_pickle=True)["arr_0"].item()

imgs = dat["imgs"]
masks_true = dat["masks_true"]

plt.figure(figsize=(8, 3))
for i, iex in enumerate([9, 16, 21]):
    img = imgs[iex].squeeze()
    plt.subplot(1, 3, 1 + i)
    plt.imshow(img[0], cmap="gray", vmin=0, vmax=1)
    plt.axis("off")
plt.tight_layout()
plt.show()

"""### Run Cellpose-SAM"""

masks_pred, flows, styles = model.eval(imgs, niter=1000)  # using more iterations for bacteria

"""plot results"""

from cellpose import transforms, plot

titles = [
    "Cellpose",
    "Nuclei",
    "Tissuenet",
    "Livecell",
    "YeaZ",
    "Omnipose\nphase-contrast",
    "Omnipose\nfluorescent",
    "DeepBacs",
]

plt.figure(figsize=(12, 6))
ly = 400
for iex in range(len(imgs)):
    img = imgs[iex].squeeze().copy()
    img = np.clip(
        transforms.normalize_img(img, axis=0), 0, 1
    )  # normalize images across channel axis
    ax = plt.subplot(3, 8, (iex % 3) * 8 + (iex // 3) + 1)
    if img[1].sum() == 0:
        img = img[0]
        ax.imshow(img, cmap="gray")
    else:
        # make RGB from 2 channel image
        img = np.concatenate((np.zeros_like(img)[:1], img), axis=0).transpose(1, 2, 0)
        ax.imshow(img)
    ax.set_ylim([0, min(400, img.shape[0])])
    ax.set_xlim([0, min(400, img.shape[1])])

    # GROUND-TRUTH = PURPLE
    # PREDICTED = YELLOW
    outlines_gt = utils.outlines_list(masks_true[iex])
    outlines_pred = utils.outlines_list(masks_pred[iex])
    for o in outlines_gt:
        plt.plot(o[:, 0], o[:, 1], color=[0.7, 0.4, 1], lw=0.5)
    for o in outlines_pred:
        plt.plot(o[:, 0], o[:, 1], color=[1, 1, 0.3], lw=0.75, ls="--")
    plt.axis("off")

    if iex % 3 == 0:
        ax.set_title(titles[iex // 3])

plt.tight_layout()
plt.show()

"""# Run Cellpose-SAM in 3D

There are two ways to run cellpose in 3D, this cell shows both, choose which one works best for you.

First way: computes flows from 2D slices and combines into 3D flows to create masks


"""

img_3D = io.imread("rgb_3D.tif")


# 1. computes flows from 2D slices and combines into 3D flows to create masks
masks, flows, _ = model.eval(
    img_3D, z_axis=0, channel_axis=1, batch_size=32, do_3D=True, flow3D_smooth=1
)

"""Second way: computes masks in 2D slices and stitches masks in 3D based on mask overlap

Note stitching (with stitch_threshold > 0) can also be used to track cells over time.
"""

# 2. computes masks in 2D slices and stitches masks in 3D based on mask overlap
print("running cellpose 2D + stitching masks")
masks_stitched, flows_stitched, _ = model.eval(
    img_3D, z_axis=0, channel_axis=1, batch_size=32, do_3D=False, stitch_threshold=0.5
)

"""Results from 3D flows => masks computation"""

# DISPLAY RESULTS 3D flows => masks
plt.figure(figsize=(15, 3))
for i, iplane in enumerate(np.arange(0, 75, 10, int)):
    img0 = plot.image_to_rgb(img_3D[iplane, [1, 0]].copy(), channels=[2, 3])
    plt.subplot(1, 8, i + 1)
    outlines = utils.masks_to_outlines(masks[iplane])
    outX, outY = np.nonzero(outlines)
    imgout = img0.copy()
    imgout[outX, outY] = np.array([255, 75, 75])
    plt.imshow(imgout)
    plt.title("iplane = %d" % iplane)

"""Results from stitching"""

# DISPLAY RESULTS stitching
plt.figure(figsize=(15, 3))
for i, iplane in enumerate(np.arange(0, 75, 10, int)):
    img0 = plot.image_to_rgb(img_3D[iplane, [1, 0]].copy(), channels=[2, 3])
    plt.subplot(1, 8, i + 1)
    outlines = utils.masks_to_outlines(masks_stitched[iplane])
    outX, outY = np.nonzero(outlines)
    imgout = img0.copy()
    imgout[outX, outY] = np.array([255, 75, 75])
    plt.imshow(imgout)
    plt.title("iplane = %d" % iplane)
