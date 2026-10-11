<!-- MarkdownTOC -->

- [IHC4BC       @ visualize_tasks](#ihc4bc___visualize_task_s_)
    - [HandE       @ IHC4BC](#hande___ihc4bc_)
    - [IHC       @ IHC4BC](#ihc___ihc4bc_)
- [HNSCC       @ visualize_tasks](#hnscc___visualize_task_s_)
    - [A11       @ HNSCC](#a11___hnsc_c_)
    - [multi-256-batch       @ HNSCC](#multi_256_batch___hnsc_c_)
- [NSCLC       @ visualize_tasks](#nsclc___visualize_task_s_)
    - [B10       @ NSCLC](#b10___nscl_c_)
    - [B11       @ NSCLC](#b11___nscl_c_)
    - [multi-256-batch       @ NSCLC](#multi_256_batch___nscl_c_)
- [Cervix       @ visualize_tasks](#cervix___visualize_task_s_)
    - [C10       @ Cervix](#c10___cervix_)
    - [C11       @ Cervix](#c11___cervix_)
    - [multi-256       @ Cervix](#multi_256___cervix_)
    - [multi-256-batch       @ Cervix](#multi_256_batch___cervix_)
        - [grouped       @ multi-256-batch/Cervix](#grouped___multi_256_batch_cervix_)
- [UpperGI       @ visualize_tasks](#uppergi___visualize_task_s_)
    - [E10       @ UpperGI](#e10___upperg_i_)
    - [E11       @ UpperGI](#e11___upperg_i_)
    - [multi-256-batch       @ UpperGI](#multi_256_batch___upperg_i_)
- [TNBC       @ visualize_tasks](#tnbc___visualize_task_s_)
    - [1024       @ TNBC](#1024___tnbc_)
    - [512       @ TNBC](#512___tnbc_)
    - [256       @ TNBC](#256___tnbc_)
    - [multi-256-batch       @ TNBC](#multi_256_batch___tnbc_)
- [TNBC-D10       @ visualize_tasks](#tnbc_d10___visualize_task_s_)
    - [1024       @ TNBC-D10](#1024___tnbc_d10_)
    - [512       @ TNBC-D10](#512___tnbc_d10_)
        - [ensemble       @ 512/TNBC-D10](#ensemble___512_tnbc_d10_)
    - [256       @ TNBC-D10](#256___tnbc_d10_)
- [TNBC-HandE-D10       @ visualize_tasks](#tnbc_hande_d10___visualize_task_s_)
    - [256       @ TNBC-HandE-D10](#256___tnbc_hande_d10_)
    - [512       @ TNBC-HandE-D10](#512___tnbc_hande_d10_)
    - [1024       @ TNBC-HandE-D10](#1024___tnbc_hande_d10_)
- [TNBC-HandE-gbt_x99       @ visualize_tasks](#tnbc_hande_gbt_x99___visualize_task_s_)
    - [1024       @ TNBC-HandE-gbt_x99](#1024___tnbc_hande_gbt_x99_)
    - [512       @ TNBC-HandE-gbt_x99](#512___tnbc_hande_gbt_x99_)
    - [256       @ TNBC-HandE-gbt_x99](#256___tnbc_hande_gbt_x99_)
- [OCTOBER_2024-ER       @ create_tasks](#october_2024_er___create_tasks_)
    - [multi-256       @ OCTOBER_2024-ER](#multi_256___october_2024_e_r_)
        - [grouped       @ multi-256/OCTOBER_2024-ER](#grouped___multi_256_october_2024_e_r_)
    - [multi-256-batch       @ OCTOBER_2024-ER](#multi_256_batch___october_2024_e_r_)
        - [cellpose-ensemble       @ multi-256-batch/OCTOBER_2024-ER](#cellpose_ensemble___multi_256_batch_october_2024_e_r_)
    - [multi-256-batch       @ OCTOBER_2024-ER](#multi_256_batch___october_2024_e_r__1)
- [OCTOBER_2024-PR       @ create_tasks](#october_2024_pr___create_tasks_)
    - [multi-256       @ OCTOBER_2024-PR](#multi_256___october_2024_p_r_)
        - [grouped       @ multi-256/OCTOBER_2024-PR](#grouped___multi_256_october_2024_p_r_)
    - [multi-256-batch       @ OCTOBER_2024-PR](#multi_256_batch___october_2024_p_r_)
        - [cellpose-ensemble       @ multi-256-batch/OCTOBER_2024-PR](#cellpose_ensemble___multi_256_batch_october_2024_p_r_)
    - [multi-256-batch       @ OCTOBER_2024-PR](#multi_256_batch___october_2024_p_r__1)
- [OCTOBER_2024-Ki67       @ create_tasks](#october_2024_ki67___create_tasks_)
    - [multi-256       @ OCTOBER_2024-Ki67](#multi_256___october_2024_ki6_7_)
        - [grouped       @ multi-256/OCTOBER_2024-Ki67](#grouped___multi_256_october_2024_ki6_7_)
    - [multi-256-batch       @ OCTOBER_2024-Ki67](#multi_256_batch___october_2024_ki6_7_)
        - [cellpose-ensemble       @ multi-256-batch/OCTOBER_2024-Ki67](#cellpose_ensemble___multi_256_batch_october_2024_ki6_7_)

<!-- /MarkdownTOC -->


<a id="ihc4bc___visualize_task_s_"></a>
# IHC4BC       @ visualize_tasks-->cvat_auto
<a id="hande___ihc4bc_"></a>
## HandE       @ IHC4BC-->cvataa_vis
python cvataa/visualize_tasks.py root_dir=/data/IHC4BC project_name=IHC4BC-HandE directory=HandE model_suffixes=stardist,instanseg recursive=1
python cvataa/visualize_tasks.py root_dir=/data/IHC4BC project_name=IHC4BC-HandE directory=HandE model_suffixes=cellpose recursive=1
<a id="ihc___ihc4bc_"></a>
## IHC       @ IHC4BC-->cvataa_vis
python cvataa/visualize_tasks.py root_dir=/data/IHC4BC project_name=IHC4BC-IHC directory=IHC model_suffixes=stardist,instanseg recursive=1
python cvataa/visualize_tasks.py root_dir=/data/IHC4BC project_name=IHC4BC-IHC directory=IHC model_suffixes=cellpose recursive=1

<a id="hnscc___visualize_task_s_"></a>
# HNSCC       @ visualize_tasks-->cvat_auto
python cvataa/visualize_tasks.py project_name=PDL1-2026-HNSCC directory=HNSCC-Tiles model_suffixes=ensemble,stardist,instanseg 
python cvataa/visualize_tasks.py project_name=PDL1-2026-HNSCC directory=HNSCC-Tiles model_suffixes=stardist,instanseg grouped=1
<a id="a11___hnsc_c_"></a>
## A11       @ HNSCC-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-HNSCC-512 directory=HNSCC-Tiles model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=A11
<a id="multi_256_batch___hnsc_c_"></a>
## multi-256-batch       @ HNSCC-->cvataa_vis
python cvataa/visualize_tasks_batch.py project_name=PDL1-2026-HNSCC-256 directory=HNSCC-Tiles/256 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=0 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=1 max_samples=1000

<a id="nsclc___visualize_task_s_"></a>
# NSCLC       @ visualize_tasks-->cvat_auto
<a id="b10___nscl_c_"></a>
## B10       @ NSCLC-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-NSCLC-512 directory=NSCLC-Tiles model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=B10
<a id="b11___nscl_c_"></a>
## B11       @ NSCLC-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-NSCLC-512 directory=NSCLC-Tiles model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=B11
<a id="multi_256_batch___nscl_c_"></a>
## multi-256-batch       @ NSCLC-->cvataa_vis
python cvataa/visualize_tasks_batch.py project_name=PDL1-2026-NSCLC-256 directory=NSCLC-Tiles/256 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=0 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=1 max_samples=1000

<a id="cervix___visualize_task_s_"></a>
# Cervix       @ visualize_tasks-->cvat_auto
<a id="c10___cervix_"></a>
## C10       @ Cervix-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-Cervix-512 directory=Cervix-Tiles/512 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=C10
<a id="c11___cervix_"></a>
## C11       @ Cervix-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-Cervix-512 directory=Cervix-Tiles/512 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=C11
<a id="multi_256___cervix_"></a>
## multi-256       @ Cervix-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-Cervix-256 directory=Cervix-Tiles/256 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit end_frame_id=-1 end_dir_id=-1 chunk_id=0 save_metadata=1 load_existing=0
<a id="multi_256_batch___cervix_"></a>
## multi-256-batch       @ Cervix-->cvataa_vis
python cvataa/visualize_tasks_batch.py project_name=PDL1-2026-Cervix-256 directory=Cervix-Tiles/256 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=0 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=1 max_samples=1000

<a id="grouped___multi_256_batch_cervix_"></a>
### grouped       @ multi-256-batch/Cervix-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-Cervix-256 directory=Cervix-Tiles/256 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit end_frame_id=-1 end_dir_id=-1 chunk_id=0 save_metadata=1 load_existing=0 grouped=1


<a id="uppergi___visualize_task_s_"></a>
# UpperGI       @ visualize_tasks-->cvat_auto
<a id="e10___upperg_i_"></a>
## E10       @ UpperGI-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-UpperGI-512 directory=UpperGI-Tiles model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=E10
<a id="e11___upperg_i_"></a>
## E11       @ UpperGI-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-UpperGI-512 directory=UpperGI-Tiles model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=E11
<a id="multi_256_batch___upperg_i_"></a>
## multi-256-batch       @ UpperGI-->cvataa_vis
python cvataa/visualize_tasks_batch.py project_name=PDL1-2026-UpperGI-256 directory=UpperGI-Tiles/256 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=0 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=0 max_samples=1000 save_to_cache=1

<a id="tnbc___visualize_task_s_"></a>
# TNBC       @ visualize_tasks-->cvat_auto
<a id="1024___tnbc_"></a>
## 1024       @ TNBC-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=stardist,instanseg
<a id="512___tnbc_"></a>
## 512       @ TNBC-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=stardist,instanseg
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=stardist,instanseg grouped=1
<a id="256___tnbc_"></a>
## 256       @ TNBC-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg port=5151 chunk_id=0
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg port=5152 chunk_id=0 grouped=1
<a id="multi_256_batch___tnbc_"></a>
## multi-256-batch       @ TNBC-->cvataa_vis
python cvataa/visualize_tasks_batch.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=21 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=0 max_samples=1000 save_to_cache=1

<a id="tnbc_d10___visualize_task_s_"></a>
# TNBC-D10       @ visualize_tasks-->cvat_auto
<a id="1024___tnbc_d10_"></a>
## 1024       @ TNBC-D10-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10

python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-1024 directory=TNBC-Tiles/1024 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 grouped=1


<a id="512___tnbc_d10_"></a>
## 512       @ TNBC-D10-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10

python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 grouped=1

<a id="ensemble___512_tnbc_d10_"></a>
### ensemble       @ 512/TNBC-D10-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-512 directory=TNBC-Tiles/512 model_suffixes=cellpose,ensemble filter.iall=D10
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=cellpose,ensemble filter.iall=D10


<a id="256___tnbc_d10_"></a>
## 256       @ TNBC-D10-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=0
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=0 grouped=1

python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=1
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=1 grouped=1

python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=2
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=2 grouped=1

python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=3
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=3 grouped=1

python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=3 grouped=1

python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-256 directory=TNBC-Tiles/256 model_suffixes=multi,ensemble multi_labels=cellpose filter.iall=D10 end_frame_id=10


<a id="tnbc_hande_d10___visualize_task_s_"></a>
# TNBC-HandE-D10       @ visualize_tasks-->cvat_auto
<a id="256___tnbc_hande_d10_"></a>
## 256       @ TNBC-HandE-D10-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=0
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=1
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10 chunk_id=2
<a id="512___tnbc_hande_d10_"></a>
## 512       @ TNBC-HandE-D10-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-HandE-512 directory=TNBC-HandE-Tiles/512 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10
<a id="1024___tnbc_hande_d10_"></a>
## 1024       @ TNBC-HandE-D10-->cvataa_vis
python cvataa/visualize_tasks.py project_name=PDL1-2026-TNBC-HandE-1024 directory=TNBC-HandE-Tiles/1024 model_suffixes=stardist,instanseg,cellpose,cellvit filter.iall=D10

<a id="tnbc_hande_gbt_x99___visualize_task_s_"></a>
# TNBC-HandE-gbt_x99       @ visualize_tasks-->cvat_auto
<a id="1024___tnbc_hande_gbt_x99_"></a>
## 1024       @ TNBC-HandE-gbt_x99-->cvataa_vis
python cvataa/visualize_tasks.py cfg=gbt_x99 project_name=PDL1-2026-TNBC-HandE-1024 directory=TNBC-HandE-Tiles/1024 model_suffixes=stardist,instanseg filter.iall=D10
<a id="512___tnbc_hande_gbt_x99_"></a>
## 512       @ TNBC-HandE-gbt_x99-->cvataa_vis
python cvataa/visualize_tasks.py cfg=gbt_x99 project_name=PDL1-2026-TNBC-HandE-512 directory=TNBC-HandE-Tiles/512 model_suffixes=stardist,instanseg filter.iall=D10
<a id="256___tnbc_hande_gbt_x99_"></a>
## 256       @ TNBC-HandE-gbt_x99-->cvataa_vis
python cvataa/visualize_tasks.py cfg=gbt_x99 project_name=PDL1-2026-TNBC-HandE-256 directory=TNBC-HandE-Tiles/256 model_suffixes=stardist,instanseg filter.iall=D10 chunk_id=0

<a id="october_2024_er___create_tasks_"></a>
# OCTOBER_2024-ER       @ create_tasks-->cvataa_create
<a id="multi_256___october_2024_e_r_"></a>
## multi-256       @ OCTOBER_2024-ER-->cvataa_vis
python cvataa/visualize_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-ER-256 directory=OCTOBER_2024_TILES_256/ER model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit end_frame_id=-1 end_dir_id=0 chunk_id=0 save_metadata=1 load_existing=1
<a id="grouped___multi_256_october_2024_e_r_"></a>
### grouped       @ multi-256/OCTOBER_2024-ER-->cvataa_vis
python cvataa/visualize_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-ER-256 directory=OCTOBER_2024_TILES_256/ER model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit end_frame_id=-1 end_dir_id=0 chunk_id=0 save_metadata=1 load_existing=1 grouped=1
<a id="multi_256_batch___october_2024_e_r_"></a>
## multi-256-batch       @ OCTOBER_2024-ER-->cvataa_vis
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-ER-256 directory=OCTOBER_2024_TILES_256/ER model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=43 end_dir_id=-1 chunk_id=0 save_metadata=1 load_existing=0 remove_existing=1 level=2 grouped=2 
<a id="cellpose_ensemble___multi_256_batch_october_2024_e_r_"></a>
### cellpose-ensemble       @ multi-256-batch/OCTOBER_2024-ER-->cvataa_vis
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-ER-256 directory=OCTOBER_2024_TILES_256/ER model_suffixes=multi,ensemble multi_labels=cellpose start_dir_id=20 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=2 end_task_id=-1 end_dir_id=20 load_from_cache=1 max_samples=0 cols=0000ff,ff00ff
<a id="multi_256_batch___october_2024_e_r__1"></a>
## multi-256-batch       @ OCTOBER_2024-ER-->cvataa_vis
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-ER-256 directory=OCTOBER_2024_TILES_256/ER model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=11 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=0 max_samples=1000 save_to_cache=1
`load_from_cache`
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-ER-256 directory=OCTOBER_2024_TILES_256/ER model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=31 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=1 max_samples=1000


<a id="october_2024_pr___create_tasks_"></a>
# OCTOBER_2024-PR       @ create_tasks-->cvataa_create
<a id="multi_256___october_2024_p_r_"></a>
## multi-256       @ OCTOBER_2024-PR-->cvataa_vis
python cvataa/visualize_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit end_frame_id=10 end_dir_id=0 chunk_id=0 save_metadata=1
<a id="grouped___multi_256_october_2024_p_r_"></a>
### grouped       @ multi-256/OCTOBER_2024-PR-->cvataa_vis
python cvataa/visualize_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit end_frame_id=10 end_dir_id=0 chunk_id=1 save_metadata=1 grouped=1 load_existing=0
<a id="multi_256_batch___october_2024_p_r_"></a>
## multi-256-batch       @ OCTOBER_2024-PR-->cvataa_vis
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=38 chunk_id=0 save_metadata=1 remove_existing=1 level=2 grouped=2 end_task_id=-1 end_dir_id=-1
<a id="cellpose_ensemble___multi_256_batch_october_2024_p_r_"></a>
### cellpose-ensemble       @ multi-256-batch/OCTOBER_2024-PR-->cvataa_vis
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=multi,ensemble multi_labels=cellpose start_dir_id=20 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=0 end_task_id=-1 end_dir_id=20 load_from_cache=1 max_samples=0 cols=0000ff,ff00ff
<a id="multi_256_batch___october_2024_p_r__1"></a>
## multi-256-batch       @ OCTOBER_2024-PR-->cvataa_vis
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-PR-256 directory=OCTOBER_2024_TILES_256/PR model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=0 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=1 max_samples=1000

<a id="october_2024_ki67___create_tasks_"></a>
# OCTOBER_2024-Ki67       @ create_tasks-->cvataa_create
<a id="multi_256___october_2024_ki6_7_"></a>
## multi-256       @ OCTOBER_2024-Ki67-->cvataa_vis
python cvataa/visualize_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit end_frame_id=10 end_dir_id=0 chunk_id=0 save_metadata=1 remove_existing=1
<a id="grouped___multi_256_october_2024_ki6_7_"></a>
### grouped       @ multi-256/OCTOBER_2024-Ki67-->cvataa_vis
python cvataa/visualize_tasks.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit end_frame_id=10 end_dir_id=0 chunk_id=0 save_metadata=1 remove_existing=1 grouped=1
<a id="multi_256_batch___october_2024_ki6_7_"></a>
## multi-256-batch       @ OCTOBER_2024-Ki67-->cvataa_vis
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=multi multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=27 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=1 end_task_id=-1 end_dir_id=-1 load_from_cache=1 max_samples=1000
`dbg`
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=multi,ensemble multi_labels=instanseg,stardist,cellpose,cellvit start_dir_id=0 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=0 end_task_id=-1 end_dir_id=0 max_samples=0 load_from_cache=1
<a id="cellpose_ensemble___multi_256_batch_october_2024_ki6_7_"></a>
### cellpose-ensemble       @ multi-256-batch/OCTOBER_2024-Ki67-->cvataa_vis
python cvataa/visualize_tasks_batch.py root_dir=/data/BreastCancerWSIs project_name=OCTOBER_2024-Ki67-256 directory=OCTOBER_2024_TILES_256/Ki67 model_suffixes=multi,ensemble multi_labels=cellpose start_dir_id=20 chunk_id=0 save_metadata=1 remove_existing=1 level=0 grouped=2 end_task_id=-1 end_dir_id=20 load_from_cache=1 max_samples=0 cols=0000ff,ff00ff




