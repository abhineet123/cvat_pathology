<!-- MarkdownTOC -->

- [IHC4BC       @ create_tasks](#ihc4bc___create_tasks_)
    - [HandE       @ IHC4BC](#hande___ihc4bc_)
    - [IHC       @ IHC4BC](#ihc___ihc4bc_)
- [Cervix       @ create_tasks](#cervix___create_tasks_)
    - [256       @ Cervix](#256___cervix_)
        - [ensemble       @ 256/Cervix](#ensemble___256_cervix_)
        - [multi       @ 256/Cervix](#multi___256_cervix_)
    - [512       @ Cervix](#512___cervix_)
        - [ensemble       @ 512/Cervix](#ensemble___512_cervix_)
        - [multi       @ 512/Cervix](#multi___512_cervix_)
    - [1024       @ Cervix](#1024___cervix_)
- [HNSCC       @ create_tasks](#hnscc___create_tasks_)
    - [multi-256       @ HNSCC](#multi_256___hnsc_c_)
        - [ensemble       @ multi-256/HNSCC](#ensemble___multi_256_hnsc_c_)
    - [512       @ HNSCC](#512___hnsc_c_)
- [NSCLC       @ create_tasks](#nsclc___create_tasks_)
    - [multi-256       @ NSCLC](#multi_256___nscl_c_)
        - [ensemble       @ multi-256/NSCLC](#ensemble___multi_256_nscl_c_)
    - [256       @ NSCLC](#256___nscl_c_)
        - [ensemble       @ 256/NSCLC](#ensemble___256_nscl_c_)
        - [multi       @ 256/NSCLC](#multi___256_nscl_c_)
    - [512       @ NSCLC](#512___nscl_c_)
- [UpperGI       @ create_tasks](#uppergi___create_tasks_)
    - [256       @ UpperGI](#256___upperg_i_)
        - [ensemble       @ 256/UpperGI](#ensemble___256_upperg_i_)
        - [multi       @ 256/UpperGI](#multi___256_upperg_i_)
    - [512       @ UpperGI](#512___upperg_i_)
- [TNBC-D10       @ create_tasks](#tnbc_d10___create_tasks_)
    - [256       @ TNBC-D10](#256___tnbc_d10_)
    - [512       @ TNBC-D10](#512___tnbc_d10_)
        - [ensemble       @ 512/TNBC-D10](#ensemble___512_tnbc_d10_)
        - [multi       @ 512/TNBC-D10](#multi___512_tnbc_d10_)
    - [1024       @ TNBC-D10](#1024___tnbc_d10_)
- [TNBC       @ create_tasks](#tnbc___create_tasks_)
    - [256       @ TNBC](#256___tnbc_)
        - [multi       @ 256/TNBC](#multi___256_tnbc_)
        - [ensemble       @ 256/TNBC](#ensemble___256_tnbc_)
    - [512       @ TNBC](#512___tnbc_)
        - [multi       @ 512/TNBC](#multi___512_tnbc_)
    - [1024       @ TNBC](#1024___tnbc_)
- [TNBC-HandE       @ create_tasks](#tnbc_hande___create_tasks_)
    - [256       @ TNBC-HandE](#256___tnbc_hande_)
    - [512       @ TNBC-HandE](#512___tnbc_hande_)
    - [1024       @ TNBC-HandE](#1024___tnbc_hande_)
- [OCTOBER_2024       @ create_tasks](#october_2024___create_tasks_)
    - [multi-256       @ OCTOBER_2024](#multi_256___october_2024_)
    - [ensemble-256       @ OCTOBER_2024](#ensemble_256___october_2024_)

<!-- /MarkdownTOC -->

<a id="ihc4bc___create_tasks_"></a>
# IHC4BC       @ create_tasks-->cvataa_create
<a id="hande___ihc4bc_"></a>
## HandE       @ IHC4BC-->cvataa_create
python cvataa/create_tasks.py root_dir=/data/IHC4BC project_name=IHC4BC-HandE directory=HandE model_suffixes=instanseg,stardist recursive=1
python cvataa/create_tasks.py root_dir=/data/IHC4BC project_name=IHC4BC-HandE directory=HandE model_suffixes=cellpose recursive=1
<a id="ihc___ihc4bc_"></a>
## IHC       @ IHC4BC-->cvataa_create
python cvataa/create_tasks.py root_dir=/data/IHC4BC project_name=IHC4BC-IHC directory=IHC model_suffixes=instanseg,stardist recursive=1
python cvataa/create_tasks.py root_dir=/data/IHC4BC project_name=IHC4BC-IHC directory=IHC model_suffixes=cellpose recursive=1

<a id="cervix___create_tasks_"></a>
# Cervix       @ create_tasks-->cvataa_create

<a id="256___cervix_"></a>
## 256       @ Cervix-->cvataa_create
<a id="ensemble___256_cervix_"></a>
### ensemble       @ 256/Cervix-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-Cervix-256 directory=Cervix-Tiles/256 model_suffixes=ensemble @chunk size=1000 tolerance=0 @ start_dir_id=0
<a id="multi___256_cervix_"></a>
### multi       @ 256/Cervix-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-Cervix-256 directory=Cervix-Tiles/256 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 @chunk size=1000 tolerance=0

<a id="512___cervix_"></a>
## 512       @ Cervix-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-Cervix-512 directory=Cervix-Tiles/512 model_suffixes=instanseg,stardist,cellpose,cellvit
<a id="ensemble___512_cervix_"></a>
### ensemble       @ 512/Cervix-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-Cervix-512 directory=Cervix-Tiles/512 model_suffixes=ensemble chunk.size=1000
<a id="multi___512_cervix_"></a>
### multi       @ 512/Cervix-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-Cervix-512 directory=Cervix-Tiles/512 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1

<a id="1024___cervix_"></a>
## 1024       @ Cervix-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-Cervix-1024 directory=Cervix-Tiles/1024 model_suffixes=instanseg,stardist,cellpose,cellvit

<a id="hnscc___create_tasks_"></a>
# HNSCC       @ create_tasks-->cvataa_create
<a id="512___hnsc_c_"></a>
<a id="multi_256___hnsc_c_"></a>
## multi-256       @ HNSCC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-256 directory=HNSCC-Tiles/256 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 @chunk size=1000 tolerance=0
<a id="ensemble___multi_256_hnsc_c_"></a>
### ensemble       @ multi-256/HNSCC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-256 directory=HNSCC-Tiles/256 model_suffixes=ensemble @chunk size=1000 tolerance=0 @ start_dir_id=11

<a id="512___hnsc_c_"></a>
## 512       @ HNSCC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=instanseg,stardist,cellpose,cellvit

python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=stardist filter.iall=A11
python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=instanseg filter.iall=A11

python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=cellpose,cellvit

<a id="nsclc___create_tasks_"></a>
# NSCLC       @ create_tasks-->cvataa_create
<a id="multi_256___nscl_c_"></a>
## multi-256       @ NSCLC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-NSCLC-256 directory=NSCLC-Tiles/256 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 @chunk size=1000 tolerance=0 @ start_dir_id=6
<a id="ensemble___multi_256_nscl_c_"></a>
### ensemble       @ multi-256/NSCLC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-NSCLC-256 directory=NSCLC-Tiles/256 model_suffixes=ensemble @chunk size=1000 tolerance=0 @ start_dir_id=0
<a id="256___nscl_c_"></a>
## 256       @ NSCLC-->cvataa_create
<a id="ensemble___256_nscl_c_"></a>
### ensemble       @ 256/NSCLC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-NSCLC-256 directory=NSCLC-Tiles/256 model_suffixes=ensemble chunk.size=1000
<a id="multi___256_nscl_c_"></a>
### multi       @ 256/NSCLC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-NSCLC-256 directory=NSCLC-Tiles/256 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 chunk.size=1000

<a id="512___nscl_c_"></a>
## 512       @ NSCLC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-NSCLC-512 directory=NSCLC-Tiles model_suffixes=instanseg,stardist,cellpose,cellvit



<a id="uppergi___create_tasks_"></a>
# UpperGI       @ create_tasks-->cvataa_create
<a id="256___upperg_i_"></a>
## 256       @ UpperGI-->cvataa_create
<a id="ensemble___256_upperg_i_"></a>
### ensemble       @ 256/UpperGI-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-UpperGI-256 directory=UpperGI-Tiles/256 model_suffixes=ensemble @chunk size=1000 tolerance=0 @ start_dir_id=29
`dbg`
python cvataa/create_tasks.py project_name=PDL1-2026-UpperGI-256 directory=UpperGI-Tiles/256 model_suffixes=ensemble @chunk size=1000 tolerance=0 @ filter.iall=E13 start_dir_id=4
<a id="multi___256_upperg_i_"></a>
### multi       @ 256/UpperGI-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-UpperGI-256 directory=UpperGI-Tiles/256 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 @chunk size=1000 tolerance=0

<a id="512___upperg_i_"></a>
## 512       @ UpperGI-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-UpperGI-512 directory=UpperGI-Tiles model_suffixes=instanseg,stardist,cellpose,cellvit

<a id="tnbc_d10___create_tasks_"></a>
# TNBC-D10       @ create_tasks-->cvataa_create
<a id="256___tnbc_d10_"></a>
## 256       @ TNBC-D10-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=cellvit chunk.size=500 filter.iall=D10
<a id="512___tnbc_d10_"></a>
## 512       @ TNBC-D10-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=instanseg,stardist,cellpose filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=cellvit filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=microsam filter.iall=D10

<a id="ensemble___512_tnbc_d10_"></a>
### ensemble       @ 512/TNBC-D10-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=ensemble filter.iall=D10 chunk.size=1000

<a id="multi___512_tnbc_d10_"></a>
### multi       @ 512/TNBC-D10-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=instanseg,stardist,cellpose,cellvit filter.iall=D10 multi=1 chunk.size=1000

<a id="1024___tnbc_d10_"></a>
## 1024       @ TNBC-D10-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=cellvit filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=stardist filter.iall=D10 chunk.size=10

<a id="tnbc___create_tasks_"></a>
# TNBC       @ create_tasks-->cvataa_create
<a id="256___tnbc_"></a>
## 256       @ TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=instanseg,stardist,cellpose,cellvit,ensemble

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=instanseg,stardist,cellpose chunk.size=500
<a id="multi___256_tnbc_"></a>
### multi       @ 256/TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 chunk.size=1000
<a id="ensemble___256_tnbc_"></a>
### ensemble       @ 256/TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=ensemble


<a id="512___tnbc_"></a>
## 512       @ TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=instanseg,stardist,cellpose

<a id="multi___512_tnbc_"></a>
### multi       @ 512/TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 chunk.size=1000

<a id="1024___tnbc_"></a>
## 1024       @ TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=cellpose 

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=instanseg,stardist,cellpose 

<a id="tnbc_hande___create_tasks_"></a>
# TNBC-HandE       @ create_tasks-->cvataa_create
<a id="256___tnbc_hande_"></a>
## 256       @ TNBC-HandE-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=instanseg,stardist,cellpose chunk.size=1000

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=instanseg,stardist,cellpose chunk.size=1000 filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=cellpose chunk.size=1000 filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=cellvit chunk.size=1000 filter.iall=D10

<a id="512___tnbc_hande_"></a>
## 512       @ TNBC-HandE-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-512 directory=TNBC-HandE-Tiles/512 model_suffixes=stardist 

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-512 directory=TNBC-HandE-Tiles/512 model_suffixes=cellpose 

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-512 directory=TNBC-HandE-Tiles/512 model_suffixes=cellvit filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-512 directory=TNBC-HandE-Tiles/512 model_suffixes=microsam filter.iall=D10

<a id="1024___tnbc_hande_"></a>
## 1024       @ TNBC-HandE-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-1024 directory=TNBC-HandE-Tiles/1024 model_suffixes=instanseg,stardist,cellpose 

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-1024 directory=TNBC-HandE-Tiles/1024 model_suffixes=cellpose 

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-1024 directory=TNBC-HandE-Tiles/1024 model_suffixes=cellvit  filter.iall=D10


<a id="october_2024___create_tasks_"></a>
# OCTOBER_2024       @ create_tasks-->cvataa_create
<a id="multi_256___october_2024_"></a>
## multi-256       @ OCTOBER_2024-->cvataa_create
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-ER-256 directory=OCTOBER_2024_TILES_256/ER model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 chunk.size=1000
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 chunk.size=1000
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 chunk.size=1000
`dbg`
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 @chunk size=10 count=10 @ end_dir_id=0 start_dir_id=0

python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=instanseg,stardist,cellpose,cellvit multi=1 @chunk size=10 count=10 @ end_dir_id=0 start_dir_id=0

<a id="ensemble_256___october_2024_"></a>
## ensemble-256       @ OCTOBER_2024-->cvataa_create
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-ER-256 directory=OCTOBER_2024_TILES_256/ER model_suffixes=ensemble chunk.size=1000 start_dir_id=0
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=ensemble chunk.size=1000
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=ensemble chunk.size=1000
`dbg`
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=ensemble @chunk size=10 count=10 @ end_dir_id=0 start_dir_id=0
python cvataa/create_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=ensemble @chunk size=10 count=10 @ end_dir_id=0 start_dir_id=0

