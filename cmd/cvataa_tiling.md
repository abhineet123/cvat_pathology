<!-- MarkdownTOC -->

- [TNBC-D10       @ annotate_tasks](#tnbc_d10___annotate_tasks_)
    - [cellvit       @ TNBC-D10](#cellvit___tnbc_d10_)
        - [vis       @ cellvit/TNBC-D10](#vis___cellvit_tnbc_d10_)
        - [stitch       @ cellvit/TNBC-D10](#stitch___cellvit_tnbc_d10_)
        - [create       @ cellvit/TNBC-D10](#create___cellvit_tnbc_d10_)

<!-- /MarkdownTOC -->

<a id="tnbc_d10___annotate_tasks_"></a>
# TNBC-D10       @ annotate_tasks-->cvat_auto
<a id="cellvit___tnbc_d10_"></a>
## cellvit       @ TNBC-D10-->cvataa_tiling
<a id="vis___cellvit_tnbc_d10_"></a>
### vis       @ cellvit/TNBC-D10-->cvataa_tiling
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=cellvit filter.iall=D10 chunk_id=0 local=1

python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=cellvit filter.iall=D10 local=1
<a id="stitch___cellvit_tnbc_d10_"></a>
### stitch       @ cellvit/TNBC-D10-->cvataa_tiling
python cvataa/stitch_tiles.py tile_dir=/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit vis=32

python cvataa/stitch_tiles.py tile_dir=/home/abhineet/data/PDL1-2026-Tiles/TNBC-Tiles/1024/D10 vis=32 is_mask=0 memmap=0
python cvataa/stitch_tiles.py tile_dir=/home/abhineet/data/PDL1-2026-Tiles/TNBC-Tiles/256/D10 vis=32 is_mask=0 memmap=0
```
/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit-stiched vis=32
```


python cvataa/stitch_tiles_v2.py tile_dir=/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit wsi_path=/data/PDL1-2026/TNBC-D/D10.svs vis=0 save=1 memmap=0

<a id="create___cellvit_tnbc_d10_"></a>
### create       @ cellvit/TNBC-D10-->cvataa_tiling
python cvataa/create_tiles.py root_dir=/data/PDL1-2026-Tiles mask_path=vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit-stitched/D10.tif 

/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit-1024

python cvataa/create_mask_tiles.py root_dir=/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011 mask_path=masks-cellvit-stitched/D10.tif output_dir=masks-cellvit-unstitched-256 source_dir=/data/PDL1-2026-Tiles/TNBC-Tiles/256/D10 vis=1

python cvataa/create_mask_tiles.py root_dir=/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011 mask_path=masks-cellvit-stitched/D10.tif output_dir=masks-cellvit-unstitched-1024 source_dir=/data/PDL1-2026-Tiles/TNBC-Tiles/1024/D10 vis=1
