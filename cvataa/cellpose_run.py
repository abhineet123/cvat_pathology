import numpy as np

np.set_printoptions(legacy="1.25")

from cellpose import models, core, io, plot
from pathlib import Path
from tqdm import trange
import matplotlib.pyplot as plt
from natsort import natsorted

io.logger_setup()  # run this to get printing of progress

# Check if colab notebook instance has GPU access
if core.use_gpu() == False:
    raise ImportError("No GPU access, change your runtime")

model = models.CellposeModel(gpu=True)

"""Input directory with your images:"""

# *** change to your google drive folder path ***
dir = "/home/abhineet/data/PDL1-2026-Tiles/TNBC-HandE-Tiles/256/D10_HE/"
dir = Path(dir)
if not dir.exists():
    raise FileNotFoundError("directory does not exist")

# *** change to your image extension ***
image_ext = ".png"

# list all files
files = natsorted(
    [f for f in dir.glob("*" + image_ext) if "_masks" not in f.name and "_flows" not in f.name]
)

if len(files) == 0:
    raise FileNotFoundError(
        "no image files found, did you specify the correct folder and extension?"
    )
else:
    print(f"{len(files)} images in folder:")

for f in files:
    print(f.name)

"""## Run Cellpose-SAM on one image in folder

Here are some of the parameters you can change:

* ***flow_threshold*** is  the  maximum  allowed  error  of  the  flows  for  each  mask.   The  default  is 0.4.
    *  **Increase** this threshold if cellpose is not returning as many masks as you’d expect (or turn off completely with 0.0)
    *   **Decrease** this threshold if cellpose is returning too many ill-shaped masks.

* ***cellprob_threshold*** determines proability that a detected object is a cell.   The  default  is 0.0.
    *   **Decrease** this threshold if cellpose is not returning as many masks as you’d expect or if masks are too small
    *   **Increase** this threshold if cellpose is returning too many masks esp from dull/dim areas.

* ***tile_norm_blocksize*** determines the size of blocks used for normalizing the image. The default is 0, which means the entire image is normalized together.
  You may want to change this to 100-200 pixels if you have very inhomogeneous brightness across your image.


"""

img = io.imread(files[0])

print(
    f"your image has shape: {img.shape}. Assuming channel dimension is last with {img.shape[-1]} channels"
)

"""### Channel Selection:

- Use the dropdowns below to select the _zero-indexed_ channels of your image to segment. The order does not matter. Remember to rerun the cell after you edit the dropdowns.

- If you have a histological image taken in brightfield, you don't need to adjust the channels.

- If you have a fluroescent image with multiple stains, you should choose one channel with a cytoplasm/membrane stain, one channel with a nuclear stain, and set the third channel to `None`. Choosing multiple channels may produce segmentaiton of all the structures in the image. If you have retrained the model on your data with a thrid stain (described below), you can run segmentation with all channels.
"""

first_channel = "0"  # @param ['None', 0, 1, 2, 3, 4, 5]
second_channel = "1"  # @param ['None', 0, 1, 2, 3, 4, 5]
third_channel = "2"  # @param ['None', 0, 1, 2, 3, 4, 5]

selected_channels = []
for i, c in enumerate([first_channel, second_channel, third_channel]):
    if c == "None":
        continue
    if int(c) > img.shape[-1]:
        assert (
            False
        ), "invalid channel index, must have index greater or equal to the number of channels"
    if c != "None":
        selected_channels.append(int(c))


img_selected_channels = np.zeros_like(img)
img_selected_channels[:, :, : len(selected_channels)] = img[:, :, selected_channels]


flow_threshold = 0
cellprob_threshold = -1000
tile_norm_blocksize = 0

masks, flows, styles = model.eval(
    img_selected_channels,
    batch_size=32,
    flow_threshold=flow_threshold,
    cellprob_threshold=cellprob_threshold,
    normalize={"tile_norm_blocksize": tile_norm_blocksize},
)

fig = plt.figure(figsize=(12, 5))
plot.show_segmentation(fig, img_selected_channels, masks, flows[0])
plt.tight_layout()
plt.show()

"""## Run Cellpose-SAM on folder of images

if you have many large images, you may want to run them as a loop over images


"""

masks_ext = ".png" if image_ext == ".png" else ".tif"
for i in trange(len(files)):
    f = files[i]
    img = io.imread(f)
    masks, flows, styles = model.eval(
        img,
        batch_size=32,
        flow_threshold=flow_threshold,
        cellprob_threshold=cellprob_threshold,
        normalize={"tile_norm_blocksize": tile_norm_blocksize},
    )
    io.imsave(dir / (f.stem + "_masks" + masks_ext), masks)

"""if you have small images, you may want to load all of them first and then run, so that they can be batched together on the GPU"""

print("loading images")
imgs = [io.imread(files[i]) for i in trange(len(files))]

print("running cellpose-SAM")
masks, flows, styles = model.eval(
    imgs,
    batch_size=32,
    flow_threshold=flow_threshold,
    cellprob_threshold=cellprob_threshold,
    normalize={"tile_norm_blocksize": tile_norm_blocksize},
)

print("saving masks")
for i in trange(len(files)):
    f = files[i]
    io.imsave(dir / (f.stem + "_masks" + masks_ext), masks[i])

"""to save your masks for ImageJ, run the following code:"""

for i in trange(len(files)):
    f = files[i]
    masks0 = io.imsave(dir / (f.name + "_masks" + masks_ext))
    io.save_rois(masks0, f)
