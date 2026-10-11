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
    - [512       @ Cervix](#512___cervix_)
    - [multi-256       @ Cervix](#multi_256___cervix_)
        - [ensemble       @ multi-256/Cervix](#ensemble___multi_256_cervix_)
- [HNSCC       @ annotate_tasks](#hnscc___annotate_tasks_)
    - [multi-256       @ HNSCC](#multi_256___hnsc_c_)
        - [ensemble       @ multi-256/HNSCC](#ensemble___multi_256_hnsc_c_)
    - [512       @ HNSCC](#512___hnsc_c_)
- [NSCLC       @ annotate_tasks](#nsclc___annotate_tasks_)
    - [multi-256       @ NSCLC](#multi_256___nscl_c_)
        - [ensemble       @ multi-256/NSCLC](#ensemble___multi_256_nscl_c_)
    - [stardist-512       @ NSCLC](#stardist_512___nscl_c_)
- [UpperGI       @ annotate_tasks](#uppergi___annotate_tasks_)
    - [stardist       @ UpperGI](#stardist___upperg_i_)
    - [multi-256       @ UpperGI](#multi_256___upperg_i_)
        - [ensemble       @ multi-256/UpperGI](#ensemble___multi_256_upperg_i_)
- [TNBC       @ annotate_tasks](#tnbc___annotate_tasks_)
    - [stardist       @ TNBC](#stardist___tnbc_)
    - [instanseg       @ TNBC](#instanseg___tnbc_)
    - [cellpose       @ TNBC](#cellpose___tnbc_)
    - [multi-256       @ TNBC](#multi_256___tnbc_)
        - [ensemble       @ multi-256/TNBC](#ensemble___multi_256_tnbc_)
    - [multi-512       @ TNBC](#multi_512___tnbc_)
- [TNBC-D10       @ annotate_tasks](#tnbc_d10___annotate_tasks_)
    - [stardist       @ TNBC-D10](#stardist___tnbc_d10_)
    - [instanseg       @ TNBC-D10](#instanseg___tnbc_d10_)
    - [cellpose       @ TNBC-D10](#cellpose___tnbc_d10_)
    - [cellvit       @ TNBC-D10](#cellvit___tnbc_d10_)
        - [delete       @ cellvit/TNBC-D10](#delete___cellvit_tnbc_d10_)
    - [ensemble       @ TNBC-D10](#ensemble___tnbc_d10_)
    - [multi       @ TNBC-D10](#multi___tnbc_d10_)
        - [ensemble       @ multi/TNBC-D10](#ensemble___multi_tnbc_d10_)
- [TNBC-HandE       @ annotate_tasks](#tnbc_hande___annotate_tasks_)
    - [stardist       @ TNBC-HandE](#stardist___tnbc_hande_)
    - [instanseg       @ TNBC-HandE](#instanseg___tnbc_hande_)
    - [cellpose       @ TNBC-HandE](#cellpose___tnbc_hande_)
    - [cellvit       @ TNBC-HandE](#cellvit___tnbc_hande_)
    - [microsam       @ TNBC-HandE](#microsam___tnbc_hande_)
- [OCTOBER_2024-ER       @ create_tasks](#october_2024_er___create_tasks_)
    - [multi-256       @ OCTOBER_2024-ER](#multi_256___october_2024_e_r_)
        - [ensemble       @ multi-256/OCTOBER_2024-ER](#ensemble___multi_256_october_2024_e_r_)
- [OCTOBER_2024-PR       @ create_tasks](#october_2024_pr___create_tasks_)
    - [multi-256       @ OCTOBER_2024-PR](#multi_256___october_2024_p_r_)
        - [ensemble       @ multi-256/OCTOBER_2024-PR](#ensemble___multi_256_october_2024_p_r_)
- [OCTOBER_2024-Ki67       @ create_tasks](#october_2024_ki67___create_tasks_)
    - [multi-256       @ OCTOBER_2024-Ki67](#multi_256___october_2024_ki6_7_)
        - [ensemble       @ multi-256/OCTOBER_2024-Ki67](#ensemble___multi_256_october_2024_ki6_7_)
            - [meta       @ ensemble/multi-256/OCTOBER_2024-Ki67](#meta___ensemble_multi_256_october_2024_ki67_)

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
python cvataa/annotate_tasks.py filter.iall=HNSCC,A12,512 models=cellpose

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
<a id="512___cervix_"></a>
## 512       @ Cervix-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=Cervix filter.iany=512 filter.eall=HandE models=stardist
<a id="multi_256___cervix_"></a>
## multi-256       @ Cervix-->cvataa_annotate
CUDA_VISIBLE_DEVICES= python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=Cervix iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=Cervix iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=Cervix iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=Cervix iany=256 eall=HandE 
<a id="ensemble___multi_256_cervix_"></a>
### ensemble       @ multi-256/Cervix-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=Cervix iany=256 eall=HandE @ensemble sfx=1 multi=1

<a id="hnscc___annotate_tasks_"></a>
# HNSCC       @ annotate_tasks-->cvat_auto
<a id="multi_256___hnsc_c_"></a>
## multi-256       @ HNSCC-->cvataa_annotate
CUDA_VISIBLE_DEVICES= python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=HNSCC iany=256 eall=HandE @ start_id=868
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=HNSCC iany=256 eall=HandE @ start_id=1004
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=HNSCC iany=256 eall=HandE @ start_id=583 
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=HNSCC iany=256 eall=HandE @ start_id=972 
<a id="ensemble___multi_256_hnsc_c_"></a>
### ensemble       @ multi-256/HNSCC-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=HNSCC iany=256 eall=HandE @ensemble sfx=1 multi=1


<a id="512___hnsc_c_"></a>
## 512       @ HNSCC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=HNSCC filter.iany=512 filter.eall=HandE models=stardist

<a id="nsclc___annotate_tasks_"></a>
# NSCLC       @ annotate_tasks-->cvat_auto
<a id="multi_256___nscl_c_"></a>
## multi-256       @ NSCLC-->cvataa_annotate
CUDA_VISIBLE_DEVICES= python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=NSCLC iany=256 eall=HandE @ start_id=86 end_id=86
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=NSCLC iany=256 eall=HandE @ start_id=0
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=NSCLC iany=256 eall=HandE @ start_id=0 
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=NSCLC iany=256 eall=HandE @ start_id=0 
<a id="ensemble___multi_256_nscl_c_"></a>
### ensemble       @ multi-256/NSCLC-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=NSCLC iany=256 eall=HandE @ensemble sfx=1 multi=1

<a id="stardist_512___nscl_c_"></a>
## stardist-512       @ NSCLC-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=NSCLC filter.iany=512 filter.eall=HandE models=stardist
<a id="cellpose_wsi___nscl_c_"></a>


<a id="uppergi___annotate_tasks_"></a>
# UpperGI       @ annotate_tasks-->cvat_auto
<a id="stardist___upperg_i_"></a>
## stardist       @ UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=UpperGI filter.iany=512 filter.eall=HandE models=stardist
<a id="multi_256___upperg_i_"></a>
## multi-256       @ UpperGI-->cvataa_annotate
CUDA_VISIBLE_DEVICES= python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=UpperGI iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=UpperGI iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=UpperGI iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=UpperGI iany=256 eall=HandE 
<a id="ensemble___multi_256_upperg_i_"></a>
### ensemble       @ multi-256/UpperGI-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=UpperGI iany=256 eall=HandE @ensemble sfx=1 multi=1

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

<a id="multi_256___tnbc_"></a>
## multi-256       @ TNBC-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=TNBC iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=TNBC iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=TNBC iany=256 eall=HandE 
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=TNBC iany=256 eall=HandE 
<a id="ensemble___multi_256_tnbc_"></a>
### ensemble       @ multi-256/TNBC-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=TNBC iany=256 eall=HandE @ensemble sfx=1 multi=1 @ start_id=0

<a id="multi_512___tnbc_"></a>
## multi-512       @ TNBC-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=TNBC iany=512 eall=HandE @ delete_task=1

python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=TNBC iany=512 eall=HandE 
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=TNBC iany=512 eall=HandE 
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=TNBC iany=512 eall=HandE 

<a id="tnbc_d10___annotate_tasks_"></a>
# TNBC-D10       @ annotate_tasks-->cvat_auto
<a id="stardist___tnbc_d10_"></a>
## stardist       @ TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=256 models=stardist
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=512 models=stardist
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=1024 models=stardist
<a id="instanseg___tnbc_d10_"></a>
## instanseg       @ TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.eall=HandE filter.iany=256 models=instanseg
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
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=256 filter.eall=HandE models=cellvit
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=512 filter.eall=HandE models=cellvit
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=1024 filter.eall=HandE models=cellvit

<a id="delete___cellvit_tnbc_d10_"></a>
### delete       @ cellvit/TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=256 filter.eall=HandE models=cellvit delete=1

<a id="ensemble___tnbc_d10_"></a>
## ensemble       @ TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=TNBC,D10 iany=256 eall=HandE @ensemble sfx=1 

python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=TNBC,D10 iany=512 eall=HandE @ensemble sfx=1 

<a id="multi___tnbc_d10_"></a>
## multi       @ TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=TNBC,D10 iany=256 eall=HandE 

python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=256 filter.eall=HandE models=instanseg multi=1
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=256 filter.eall=HandE models=cellpose multi=1
python cvataa/annotate_tasks.py filter.iall=TNBC,D10 filter.iany=256 filter.eall=HandE models=cellvit multi=1

<a id="ensemble___multi_tnbc_d10_"></a>
### ensemble       @ multi/TNBC-D10-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=TNBC,D10 iany=256 eall=HandE @ensemble sfx=1 multi=1

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

<a id="microsam___tnbc_hande_"></a>
## microsam       @ TNBC-HandE-->cvataa_annotate
python cvataa/annotate_tasks.py filter.iall=TNBC-HandE,D10 filter.iany=512 models=microsam

<a id="october_2024_er___create_tasks_"></a>
# OCTOBER_2024-ER       @ create_tasks-->cvataa_create
<a id="multi_256___october_2024_e_r_"></a>
## multi-256       @ OCTOBER_2024-ER-->cvataa_annotate
CUDA_VISIBLE_DEVICES= python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=OCTOBER_2024-ER iany=256 @ start_id=1031
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=OCTOBER_2024-ER iany=256 @ start_id=648
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=OCTOBER_2024-ER iany=256 @ start_id=627
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=OCTOBER_2024-ER iany=256 @ start_id=1168
<a id="ensemble___multi_256_october_2024_e_r_"></a>
### ensemble       @ multi-256/OCTOBER_2024-ER-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=OCTOBER_2024-ER iany=256 @ensemble sfx=1 multi=1 @ start_id=0

python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=OCTOBER_2024-ER iany=256 @ensemble sfx=1 multi=1 dups=2 @ start_id=0
`meta`
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=OCTOBER_2024-ER iany=256 @ensemble sfx=1 multi=1 load=0 dups=1 @@meta cvat=2 fo=2 @ start_id=127 end_id=-1


<a id="october_2024_pr___create_tasks_"></a>
# OCTOBER_2024-PR       @ create_tasks-->cvataa_create
<a id="multi_256___october_2024_p_r_"></a>
## multi-256       @ OCTOBER_2024-PR-->cvataa_annotate
CUDA_VISIBLE_DEVICES= python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=OCTOBER_2024-PR iany=256 @ start_id=229
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=OCTOBER_2024-PR iany=256 @ start_id=423
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=OCTOBER_2024-PR iany=256 @ start_id=560
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=OCTOBER_2024-PR iany=256 @ start_id=256
<a id="ensemble___multi_256_october_2024_p_r_"></a>
### ensemble       @ multi-256/OCTOBER_2024-PR-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=OCTOBER_2024-PR iany=256 @ensemble sfx=1 multi=1 dups=1 @ start_id=0
`meta`
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=OCTOBER_2024-PR iany=256 @ensemble sfx=1 multi=1 load=0 @@meta cvat=2 fo=2 fo_root=.fiftyone_a6k shape=0 @ start_id=148 end_id=-1

<a id="october_2024_ki67___create_tasks_"></a>
# OCTOBER_2024-Ki67       @ create_tasks-->cvataa_create
<a id="multi_256___october_2024_ki6_7_"></a>
## multi-256       @ OCTOBER_2024-Ki67-->cvataa_annotate
CUDA_VISIBLE_DEVICES= python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=OCTOBER_2024-Ki67 iany=256 @ start_id=400
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=OCTOBER_2024-Ki67 iany=256 @ start_id=0
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=OCTOBER_2024-Ki67 iany=256 @ start_id=262
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=OCTOBER_2024-Ki67 iany=256 @ start_id=447
`dbg`
CUDA_VISIBLE_DEVICES= python cvataa/annotate_tasks.py models=stardist multi=1 @filter iall=OCTOBER_2024-Ki67 iany=256 @ start_id=0
python cvataa/annotate_tasks.py models=instanseg multi=1 @filter iall=OCTOBER_2024-Ki67 iany=256 @ start_id=0
python cvataa/annotate_tasks.py models=cellpose multi=1 @filter iall=OCTOBER_2024-Ki67 iany=256 @ start_id=0
python cvataa/annotate_tasks.py models=cellvit multi=1 @filter iall=OCTOBER_2024-Ki67 iany=256 @ start_id=0
<a id="ensemble___multi_256_october_2024_ki6_7_"></a>
### ensemble       @ multi-256/OCTOBER_2024-Ki67-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=OCTOBER_2024-Ki67 iany=256 @ensemble sfx=1 multi=1 dups=1 @ start_id=0
<a id="meta___ensemble_multi_256_october_2024_ki67_"></a>
#### meta       @ ensemble/multi-256/OCTOBER_2024-Ki67-->cvataa_annotate
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=OCTOBER_2024-Ki67 iany=256 @ensemble sfx=1 multi=1 dups=1 load=0 @@meta cvat=2 fo=2 shape=0 fo_root=.fiftyone_a6k @ start_id=147
`dbg`
python cvataa/annotate_tasks.py models=stardist,instanseg,cellpose,cellvit @filter iall=OCTOBER_2024-Ki67 iany=256 @ensemble sfx=1 multi=1 dups=1 load=0 @@meta cvat=2 fo=2 shape=0 @ start_id=0