<!-- MarkdownTOC -->

- [IHC4BC       @ annotate_tasks](#ihc4bc___annotate_tasks_)
    - [HandE       @ IHC4BC](#hande___ihc4bc_)
    - [IHC       @ IHC4BC](#ihc___ihc4bc_)
- [Cervix,HNSCC,NSCLC,UpperGI       @ annotate_tasks](#cervix_hnscc_nsclc_uppergi___annotate_tasks_)
    - [stardist       @ Cervix,HNSCC,NSCLC,UpperGI](#stardist___cervix_hnscc_nsclc_uppergi_)
    - [instanseg       @ Cervix,HNSCC,NSCLC,UpperGI](#instanseg___cervix_hnscc_nsclc_uppergi_)
    - [cellpose       @ Cervix,HNSCC,NSCLC,UpperGI](#cellpose___cervix_hnscc_nsclc_uppergi_)
        - [A10       @ cellpose/Cervix,HNSCC,NSCLC,UpperGI](#a10___cellpose_cervix_hnscc_nsclc_upperg_i_)
        - [A11       @ cellpose/Cervix,HNSCC,NSCLC,UpperGI](#a11___cellpose_cervix_hnscc_nsclc_upperg_i_)
        - [A12       @ cellpose/Cervix,HNSCC,NSCLC,UpperGI](#a12___cellpose_cervix_hnscc_nsclc_upperg_i_)
    - [instanseg       @ Cervix,HNSCC,NSCLC,UpperGI](#instanseg___cervix_hnscc_nsclc_uppergi__1)
        - [A10       @ instanseg/Cervix,HNSCC,NSCLC,UpperGI](#a10___instanseg_cervix_hnscc_nsclc_uppergi_)
        - [A11       @ instanseg/Cervix,HNSCC,NSCLC,UpperGI](#a11___instanseg_cervix_hnscc_nsclc_uppergi_)
    - [stardist       @ Cervix,HNSCC,NSCLC,UpperGI](#stardist___cervix_hnscc_nsclc_uppergi__1)
        - [A10       @ stardist/Cervix,HNSCC,NSCLC,UpperGI](#a10___stardist_cervix_hnscc_nsclc_upperg_i_)
        - [A11       @ stardist/Cervix,HNSCC,NSCLC,UpperGI](#a11___stardist_cervix_hnscc_nsclc_upperg_i_)
    - [cellvit       @ Cervix,HNSCC,NSCLC,UpperGI](#cellvit___cervix_hnscc_nsclc_uppergi_)
        - [A10       @ cellvit/Cervix,HNSCC,NSCLC,UpperGI](#a10___cellvit_cervix_hnscc_nsclc_uppergi_)
        - [A11       @ cellvit/Cervix,HNSCC,NSCLC,UpperGI](#a11___cellvit_cervix_hnscc_nsclc_uppergi_)
- [Cervix       @ annotate_tasks](#cervix___annotate_tasks_)
    - [stardist       @ Cervix](#stardist___cervix_)
- [HNSCC       @ annotate_tasks](#hnscc___annotate_tasks_)
    - [stardist       @ HNSCC](#stardist___hnsc_c_)
- [NSCLC       @ annotate_tasks](#nsclc___annotate_tasks_)
    - [stardist       @ NSCLC](#stardist___nscl_c_)
- [UpperGI       @ annotate_tasks](#uppergi___annotate_tasks_)
    - [stardist       @ UpperGI](#stardist___upperg_i_)
- [TNBC       @ annotate_tasks](#tnbc___annotate_tasks_)
    - [stardist       @ TNBC](#stardist___tnbc_)
    - [instanseg       @ TNBC](#instanseg___tnbc_)
    - [cellpose       @ TNBC](#cellpose___tnbc_)
- [TNBC-D10       @ annotate_tasks](#tnbc_d10___annotate_tasks_)
    - [stardist       @ TNBC-D10](#stardist___tnbc_d10_)
    - [instanseg       @ TNBC-D10](#instanseg___tnbc_d10_)
    - [cellpose       @ TNBC-D10](#cellpose___tnbc_d10_)
    - [cellvit       @ TNBC-D10](#cellvit___tnbc_d10_)
        - [load       @ cellvit/TNBC-D10](#load___cellvit_tnbc_d10_)
- [TNBC-HandE       @ annotate_tasks](#tnbc_hande___annotate_tasks_)
    - [stardist       @ TNBC-HandE](#stardist___tnbc_hande_)
    - [instanseg       @ TNBC-HandE](#instanseg___tnbc_hande_)
    - [cellpose       @ TNBC-HandE](#cellpose___tnbc_hande_)
    - [cellvit       @ TNBC-HandE](#cellvit___tnbc_hande_)

<!-- /MarkdownTOC -->

<a id="ihc4bc___annotate_tasks_"></a>
# IHC4BC       @ annotate_tasks-->cvat_auto
<a id="hande___ihc4bc_"></a>
## HandE       @ IHC4BC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=IHC4BC-HandE models=instanseg,stardist
python cvataa/annotate_tasks.py filter.iall=IHC4BC-HandE models=cellpose
`dbg`
python cvataa/annotate_tasks.py filter.iall=IHC4BC-HandE-instanseg-Her2/Patient_0_1009/Subregion_5 models=instanseg
<a id="ihc___ihc4bc_"></a>
## IHC       @ IHC4BC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=IHC4BC-IHC models=instanseg,stardist
python cvataa/annotate_tasks.py filter.iall=IHC4BC-IHC models=cellpose

<a id="cervix_hnscc_nsclc_uppergi___annotate_tasks_"></a>
# Cervix,HNSCC,NSCLC,UpperGI       @ annotate_tasks-->cvat_auto
<a id="stardist___cervix_hnscc_nsclc_uppergi_"></a>
## stardist       @ Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iany=Cervix,HNSCC,NSCLC,UpperGI filter.iall=512 filter.eall=HandE models=stardist
<a id="instanseg___cervix_hnscc_nsclc_uppergi_"></a>
## instanseg       @ Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iany=Cervix,HNSCC,NSCLC,UpperGI filter.iall=512 filter.eall=HandE models=instanseg
`done`
```
PDL1-2026-Cervix-512-instanseg-C1
PDL1-2026-Cervix-512-instanseg-C10
PDL1-2026-Cervix-512-instanseg-C11
PDL1-2026-Cervix-512-instanseg-C12
```

python cvataa/annotate_tasks.py filter.iany=HNSCC filter.iall=512, filter.eall=HandE models=instanseg

<a id="cellpose___cervix_hnscc_nsclc_uppergi_"></a>
## cellpose       @ Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iany=Cervix,HNSCC,NSCLC,UpperGI filter.iall=512 filter.eall=Cervix,C1 models=cellpose
```
PDL1-2026-Cervix-512-cellpose-C1
```
python cvataa/annotate_tasks.py filter.iany=Cervix,HNSCC,NSCLC,UpperGI filter.iall=512,Cervix,C1 filter.eall=PDL1-2026-Cervix-512-cellpose-C1 models=cellpose
```
PDL1-2026-Cervix-512-cellpose-C2
```
<a id="a10___cellpose_cervix_hnscc_nsclc_upperg_i_"></a>
### A10       @ cellpose/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A10,512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=NSCLC,B10,512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=Cervix,C10,512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=UpperGI,E10,512 models=cellpose
<a id="a11___cellpose_cervix_hnscc_nsclc_upperg_i_"></a>
### A11       @ cellpose/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A11,512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=NSCLC,B11,512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=Cervix,C11,512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=UpperGI,E11,512 models=cellpose

<a id="a12___cellpose_cervix_hnscc_nsclc_upperg_i_"></a>
### A12       @ cellpose/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A11,512 models=cellpose

<a id="instanseg___cervix_hnscc_nsclc_uppergi__1"></a>
## instanseg       @ Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
<a id="a10___instanseg_cervix_hnscc_nsclc_uppergi_"></a>
### A10       @ instanseg/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A10,512 models=instanseg
python cvataa/annotate_tasks.py filter.iall=NSCLC,B10,512 models=instanseg
python cvataa/annotate_tasks.py filter.iall=Cervix,C10,512 models=instanseg
python cvataa/annotate_tasks.py filter.iall=UpperGI,E10,512 models=instanseg
<a id="a11___instanseg_cervix_hnscc_nsclc_uppergi_"></a>
### A11       @ instanseg/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A11,512 models=instanseg
python cvataa/annotate_tasks.py filter.iall=NSCLC,B11,512 models=instanseg
python cvataa/annotate_tasks.py filter.iall=Cervix,C11,512 models=instanseg
python cvataa/annotate_tasks.py filter.iall=UpperGI,E11,512 models=instanseg

<a id="stardist___cervix_hnscc_nsclc_uppergi__1"></a>
## stardist       @ Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
<a id="a10___stardist_cervix_hnscc_nsclc_upperg_i_"></a>
### A10       @ stardist/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A10,512 models=stardist
python cvataa/annotate_tasks.py filter.iall=NSCLC,B10,512 models=stardist
python cvataa/annotate_tasks.py filter.iall=Cervix,C10,512 models=stardist
python cvataa/annotate_tasks.py filter.iall=UpperGI,E10,512 models=stardist
<a id="a11___stardist_cervix_hnscc_nsclc_upperg_i_"></a>
### A11       @ stardist/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A11,512 models=stardist
python cvataa/annotate_tasks.py filter.iall=NSCLC,B11,512 models=stardist
python cvataa/annotate_tasks.py filter.iall=Cervix,C11,512 models=stardist
python cvataa/annotate_tasks.py filter.iall=UpperGI,E11,512 models=stardist

<a id="cellvit___cervix_hnscc_nsclc_uppergi_"></a>
## cellvit       @ Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
<a id="a10___cellvit_cervix_hnscc_nsclc_uppergi_"></a>
### A10       @ cellvit/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A10,512 models=cellvit

python cvataa/annotate_tasks.py filter.iall=NSCLC,B10,512 models=cellvit
python cvataa/annotate_tasks.py filter.iall=Cervix,C10,512 models=cellvit
python cvataa/annotate_tasks.py filter.iall=UpperGI,E10,512 models=cellvit
<a id="a11___cellvit_cervix_hnscc_nsclc_uppergi_"></a>
### A11       @ cellvit/Cervix,HNSCC,NSCLC,UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC,A11,512 models=cellvit
python cvataa/annotate_tasks.py filter.iall=NSCLC,B11,512 models=cellvit
python cvataa/annotate_tasks.py filter.iall=Cervix,C11,512 models=cellvit
python cvataa/annotate_tasks.py filter.iall=UpperGI,E11,512 models=cellvit

<a id="cervix___annotate_tasks_"></a>
# Cervix       @ annotate_tasks-->cvat_auto
<a id="stardist___cervix_"></a>
## stardist       @ Cervix-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=Cervix filter.iany=512 filter.eall=HandE models=stardist

<a id="hnscc___annotate_tasks_"></a>
# HNSCC       @ annotate_tasks-->cvat_auto
<a id="stardist___hnsc_c_"></a>
## stardist       @ HNSCC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC filter.iany=512 filter.eall=HandE models=stardist

<a id="nsclc___annotate_tasks_"></a>
# NSCLC       @ annotate_tasks-->cvat_auto
<a id="stardist___nscl_c_"></a>
## stardist       @ NSCLC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=NSCLC filter.iany=512 filter.eall=HandE models=stardist

<a id="uppergi___annotate_tasks_"></a>
# UpperGI       @ annotate_tasks-->cvat_auto
<a id="stardist___upperg_i_"></a>
## stardist       @ UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=UpperGI filter.iany=512 filter.eall=HandE models=stardist

<a id="tnbc___annotate_tasks_"></a>
# TNBC       @ annotate_tasks-->cvat_auto
<a id="stardist___tnbc_"></a>
## stardist       @ TNBC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC filter.iany=256 filter.eall=HandE models=stardist
python cvataa/annotate_tasks.py filter.iall=TNBC filter.iany=256,512,1024 filter.eall=HandE models=stardist
<a id="instanseg___tnbc_"></a>
## instanseg       @ TNBC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC filter.iany=256 filter.eall=HandE models=instanseg
python cvataa/annotate_tasks.py filter.iall=TNBC filter.iany=256,512,1024 filter.eall=HandE models=instanseg
<a id="cellpose___tnbc_"></a>
## cellpose       @ TNBC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC filter.iany=256 models=cellpose
python cvataa/annotate_tasks.py filter.iall=TNBC filter.iany=512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=TNBC filter.iany=512 models=cellpose

<a id="tnbc_d10___annotate_tasks_"></a>
# TNBC-D10       @ annotate_tasks-->cvat_auto
<a id="stardist___tnbc_d10_"></a>
## stardist       @ TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=512 models=stardist
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=1024 models=stardist
<a id="instanseg___tnbc_d10_"></a>
## instanseg       @ TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=512 models=instanseg
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=1024 models=instanseg

<a id="cellpose___tnbc_d10_"></a>
## cellpose       @ TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=256 models=cellpose
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=1024 models=cellpose

<a id="cellvit___tnbc_d10_"></a>
## cellvit       @ TNBC-D10-->cvataa_annotate
`IHC and HandE`
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=256 models=cellvit
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=512 models=cellvit
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=1024 models=cellvit

<a id="load___cellvit_tnbc_d10_"></a>
### load       @ cellvit/TNBC-D10-->cvataa_annotate
python cvataa/stitch_tiles.py tile_dir=/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit vis=32

python cvataa/stitch_tiles.py tile_dir=/home/abhineet/data/PDL1-2026-Tiles/TNBC-Tiles/1024/D10 vis=32 is_mask=0 memmap=0
python cvataa/stitch_tiles.py tile_dir=/home/abhineet/data/PDL1-2026-Tiles/TNBC-Tiles/256/D10 vis=32 is_mask=0 memmap=0
```
/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit-stiched vis=32
```
python cvataa/create_tiles.py root_dir=/data/PDL1-2026-Tiles mask_path=vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit-stiched/D10.tif 

python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=1024 models=cellvit_512 load=PDL1-2026-TNBC-512-cellvit-D10-260322_170800/masks-cellvit

/data/PDL1-2026-Tiles/vis/PDL1-2026-TNBC-512-cellvit-D10-260322_171011/masks-cellvit-1024

<a id="tnbc_hande___annotate_tasks_"></a>
# TNBC-HandE       @ annotate_tasks-->cvat_auto
<a id="stardist___tnbc_hande_"></a>
## stardist       @ TNBC-HandE-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=256 models=stardist
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=512 models=stardist
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=1024 models=stardist

<a id="instanseg___tnbc_hande_"></a>
## instanseg       @ TNBC-HandE-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=256 models=instanseg
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=512 models=instanseg
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=1024 models=instanseg

<a id="cellpose___tnbc_hande_"></a>
## cellpose       @ TNBC-HandE-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=256 models=cellpose
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=512 models=cellpose
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=1024 models=cellpose

<a id="cellvit___tnbc_hande_"></a>
## cellvit       @ TNBC-HandE-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=256 models=cellvit
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE filter.iany=1024 models=cellvit

