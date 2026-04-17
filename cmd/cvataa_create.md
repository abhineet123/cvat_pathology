<!-- MarkdownTOC -->

- [IHC4BC       @ create_tasks](#ihc4bc___create_tasks_)
    - [HandE       @ IHC4BC](#hande___ihc4bc_)
    - [IHC       @ IHC4BC](#ihc___ihc4bc_)
- [Cervix       @ create_tasks](#cervix___create_tasks_)
    - [512       @ Cervix](#512___cervix_)
    - [1024       @ Cervix](#1024___cervix_)
- [HNSCC       @ create_tasks](#hnscc___create_tasks_)
    - [512       @ HNSCC](#512___hnsc_c_)
- [NSCLC       @ create_tasks](#nsclc___create_tasks_)
    - [512       @ NSCLC](#512___nscl_c_)
- [UpperGI       @ create_tasks](#uppergi___create_tasks_)
    - [512       @ UpperGI](#512___upperg_i_)
- [TNBC       @ create_tasks](#tnbc___create_tasks_)
    - [256       @ TNBC](#256___tnbc_)
    - [512       @ TNBC](#512___tnbc_)
    - [1024       @ TNBC](#1024___tnbc_)
- [TNBC-HandE       @ create_tasks](#tnbc_hande___create_tasks_)
    - [256       @ TNBC-HandE](#256___tnbc_hande_)
    - [512       @ TNBC-HandE](#512___tnbc_hande_)
    - [1024       @ TNBC-HandE](#1024___tnbc_hande_)

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
<a id="512___cervix_"></a>
## 512       @ Cervix-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-Cervix-512 directory=Cervix-Tiles/512 model_suffixes=instanseg,stardist,cellpose,cellvit
<a id="1024___cervix_"></a>
## 1024       @ Cervix-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-Cervix-1024 directory=Cervix-Tiles/1024 model_suffixes=instanseg,stardist,cellpose,cellvit
<a id="hnscc___create_tasks_"></a>
# HNSCC       @ create_tasks-->cvataa_create
<a id="512___hnsc_c_"></a>
## 512       @ HNSCC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=instanseg,stardist,cellpose,cellvit

python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=stardist filter.iall=A11
python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=instanseg filter.iall=A11

python cvataa/create_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=cellpose,cellvit
<a id="nsclc___create_tasks_"></a>
# NSCLC       @ create_tasks-->cvataa_create
<a id="512___nscl_c_"></a>
## 512       @ NSCLC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-NSCLC-512 directory=NSCLC-Tiles model_suffixes=instanseg,stardist,cellpose,cellvit
<a id="uppergi___create_tasks_"></a>
# UpperGI       @ create_tasks-->cvataa_create
<a id="512___upperg_i_"></a>
## 512       @ UpperGI-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-UpperGI-512 directory=UpperGI-Tiles model_suffixes=instanseg,stardist,cellpose,cellvit

<a id="tnbc___create_tasks_"></a>
# TNBC       @ create_tasks-->cvataa_create
<a id="256___tnbc_"></a>
## 256       @ TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=instanseg,stardist,cellpose max_images=500

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=cellvit max_images=500 filter.iall=D10

<a id="512___tnbc_"></a>
## 512       @ TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=instanseg,stardist,cellpose filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=cellvit filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=microsam filter.iall=D10

<a id="1024___tnbc_"></a>
## 1024       @ TNBC-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=cellpose 

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=instanseg,stardist,cellpose 

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=cellvit filter.iall=D10

<a id="tnbc_hande___create_tasks_"></a>
# TNBC-HandE       @ create_tasks-->cvataa_create
<a id="256___tnbc_hande_"></a>
## 256       @ TNBC-HandE-->cvataa_create
python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=instanseg,stardist,cellpose max_images=1000

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=instanseg,stardist,cellpose max_images=1000 filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=cellpose max_images=1000 filter.iall=D10

python cvataa/create_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=cellvit max_images=1000 filter.iall=D10

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
