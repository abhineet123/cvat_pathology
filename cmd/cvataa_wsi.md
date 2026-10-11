<!-- MarkdownTOC -->

- [hnscc       @ annotate_tasks](#hnscc___annotate_tasks_)
    - [clps       @ hnscc](#clps___hnsc_c_)
        - [dino       @ clps/hnscc](#dino___clps_hnscc_)
- [nsclc       @ annotate_tasks](#nsclc___annotate_tasks_)
    - [clps       @ nsclc](#clps___nscl_c_)
        - [dino       @ clps/nsclc](#dino___clps_nsclc_)
    - [cvit       @ nsclc](#cvit___nscl_c_)
        - [file_mode       @ cvit/nsclc](#file_mode___cvit_nsclc_)
- [cervix       @ annotate_tasks](#cervix___annotate_tasks_)
    - [clps       @ cervix](#clps___cervix_)
        - [dino       @ clps/cervix](#dino___clps_cervi_x_)
- [uppergi       @ annotate_tasks](#uppergi___annotate_tasks_)
    - [clps       @ uppergi](#clps___upperg_i_)
        - [dino       @ clps/uppergi](#dino___clps_uppergi_)
    - [cvit       @ uppergi](#cvit___upperg_i_)
        - [file_mode       @ cvit/uppergi](#file_mode___cvit_uppergi_)
- [tnbc       @ annotate_tasks](#tnbc___annotate_tasks_)
    - [clps       @ tnbc](#clps___tnbc_)
        - [sam       @ clps/tnbc](#sam___clps_tnb_c_)
        - [sam2       @ clps/tnbc](#sam2___clps_tnb_c_)
        - [dino       @ clps/tnbc](#dino___clps_tnb_c_)
        - [dino2       @ clps/tnbc](#dino2___clps_tnb_c_)
    - [cvit       @ tnbc](#cvit___tnbc_)
- [tnbc-he       @ annotate_tasks](#tnbc_he___annotate_tasks_)
    - [cellvit       @ tnbc-he](#cellvit___tnbc_h_e_)
- [bcw-oct       @ annotate_tasks](#bcw_oct___annotate_tasks_)
    - [clps-er       @ bcw-oct](#clps_er___bcw_oc_t_)
        - [dino       @ clps-er/bcw-oct](#dino___clps_er_bcw_oc_t_)
            - [qmlp       @ dino/clps-er/bcw-oct](#qmlp___dino_clps_er_bcw_oct_)
        - [dino2       @ clps-er/bcw-oct](#dino2___clps_er_bcw_oc_t_)
        - [sam       @ clps-er/bcw-oct](#sam___clps_er_bcw_oc_t_)
        - [sam2       @ clps-er/bcw-oct](#sam2___clps_er_bcw_oc_t_)
    - [clps-pr       @ bcw-oct](#clps_pr___bcw_oc_t_)
        - [dino       @ clps-pr/bcw-oct](#dino___clps_pr_bcw_oc_t_)
            - [qmlp       @ dino/clps-pr/bcw-oct](#qmlp___dino_clps_pr_bcw_oct_)
        - [dino2       @ clps-pr/bcw-oct](#dino2___clps_pr_bcw_oc_t_)
        - [sam       @ clps-pr/bcw-oct](#sam___clps_pr_bcw_oc_t_)
        - [sam2       @ clps-pr/bcw-oct](#sam2___clps_pr_bcw_oc_t_)
    - [clps-ki67       @ bcw-oct](#clps_ki67___bcw_oc_t_)
        - [dino       @ clps-ki67/bcw-oct](#dino___clps_ki67_bcw_oc_t_)
            - [qmlp       @ dino/clps-ki67/bcw-oct](#qmlp___dino_clps_ki67_bcw_oct_)
        - [dino2       @ clps-ki67/bcw-oct](#dino2___clps_ki67_bcw_oc_t_)
        - [sam       @ clps-ki67/bcw-oct](#sam___clps_ki67_bcw_oc_t_)
        - [sam2       @ clps-ki67/bcw-oct](#sam2___clps_ki67_bcw_oc_t_)
            - [subtype-n       @ sam2/clps-ki67/bcw-oct](#subtype_n___sam2_clps_ki67_bcw_oct_)
            - [subtype-p       @ sam2/clps-ki67/bcw-oct](#subtype_p___sam2_clps_ki67_bcw_oct_)
    - [cellvit       @ bcw-oct](#cellvit___bcw_oc_t_)
        - [file_mode       @ cellvit/bcw-oct](#file_mode___cellvit_bcw_oc_t_)
- [bcw-all       @ annotate_tasks](#bcw_all___annotate_tasks_)
    - [clps-er       @ bcw-all](#clps_er___bcw_al_l_)
        - [dino       @ clps-er/bcw-all](#dino___clps_er_bcw_al_l_)
    - [clps-pr       @ bcw-all](#clps_pr___bcw_al_l_)
        - [dino       @ clps-pr/bcw-all](#dino___clps_pr_bcw_al_l_)
    - [clps-ki67       @ bcw-all](#clps_ki67___bcw_al_l_)
        - [dino       @ clps-ki67/bcw-all](#dino___clps_ki67_bcw_al_l_)

<!-- /MarkdownTOC -->


<a id="hnscc___annotate_tasks_"></a>
# hnscc       @ annotate_tasks-->cvat_auto
<a id="clps___hnsc_c_"></a>
## clps       @ hnscc-->cvataa_wsi
<a id="dino___clps_hnscc_"></a>
### dino       @ clps/hnscc-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=pdl1:hnscc:ihc:clps-dino:batch-64:sz-8192:ov-512:end-9

CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=pdl1:hnscc:ihc:clps-dino:batch-64:sz-8192:ov-512  filter.iany+=A1,A2,A3,A4,A5,A6,A7,A8,A9 filter.eany+=A10,A20,A30
`A10,A11,A12`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=pdl1:hnscc:ihc:clps-dino:batch-64:sz-8192:ov-512 filter.iany=A10,A11,A12
`rest`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=pdl1:hnscc:ihc:clps-dino:batch-64:sz-8192:ov-512:start-15


<a id="nsclc___annotate_tasks_"></a>
# nsclc       @ annotate_tasks-->cvat_auto
<a id="clps___nscl_c_"></a>
## clps       @ nsclc-->cvataa_wsi
<a id="dino___clps_nsclc_"></a>
### dino       @ clps/nsclc-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=pdl1:nsclc:ihc:clps-dino:batch-64:sz-8192:ov-512:end-9
`B11,B12`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=pdl1:nsclc:ihc:clps-dino:batch-64:sz-8192:ov-512 filter.iany=B11,B12
`rest`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=pdl1:nsclc:ihc:clps-dino:batch-64:sz-8192:ov-512:start-18

<a id="cvit___nscl_c_"></a>
## cvit       @ nsclc-->cvataa_wsi
python cvataa/annotate_wsi.py models=cvit wsi_dir=NSCLC-B tiles_dir=NSCLC-Tiles/256 filter.eall=HE @cvit batch_size=64 @ start_id=1 @tile sz=256 ovl=64
<a id="file_mode___cvit_nsclc_"></a>
### file_mode       @ cvit/nsclc-->cvataa_wsi
python cvataa/annotate_wsi.py models=cvit wsi_dir=NSCLC-B tiles_dir=NSCLC-Tiles/256 filter.eall=HE @cvit batch_size=1 @ file_mode=1
`nucls_super`
python cvataa/annotate_wsi.py models=cvit wsi_dir=NSCLC-B tiles_dir=NSCLC-Tiles/256 filter.eall=HE @cvit batch_size=5 classifier=nucls_super chunk_size=0 @ file_mode=1 end_id=0 start_id=0
`nucls_main`
python cvataa/annotate_wsi.py models=cvit wsi_dir=NSCLC-B tiles_dir=NSCLC-Tiles/256 filter.eall=HE @cvit batch_size=5 classifier=nucls_main chunk_size=0 @ file_mode=1 end_id=1 start_id=1


<a id="cervix___annotate_tasks_"></a>
# cervix       @ annotate_tasks-->cvat_auto
<a id="clps___cervix_"></a>
## clps       @ cervix-->cvataa_wsi
<a id="dino___clps_cervi_x_"></a>
### dino       @ clps/cervix-->cvataa_wsi
`C2 to C11 except C6`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=pdl1:cervix:ihc:clps-dino:batch-64:sz-8192:ov-512:end-10:start-1:eany-C6
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=pdl1:cervix:ihc:clps-dino:batch-64:sz-8192:ov-512 filter.iany=C12
`rest`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=pdl1:cervix:ihc:clps-dino:batch-64:sz-8192:ov-512:start-18

<a id="uppergi___annotate_tasks_"></a>
# uppergi       @ annotate_tasks-->cvat_auto
<a id="clps___upperg_i_"></a>
## clps       @ uppergi-->cvataa_wsi
<a id="dino___clps_uppergi_"></a>
### dino       @ clps/uppergi-->cvataa_wsi
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=pdl1:uppergi:ihc:clps-dino:batch-64:sz-8192:ov-512:end-7:eany-E6
`E10`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=pdl1:uppergi:ihc:clps-dino:batch-64:sz-8192:ov-512:iany-E10
`rest`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=pdl1:uppergi:ihc:clps-dino:batch-64:sz-8192:ov-512:start-35

<a id="cvit___upperg_i_"></a>
## cvit       @ uppergi-->cvataa_wsi
python cvataa/annotate_wsi.py models=cvit wsi_dir=UpperGI-E tiles_dir=UpperGI-Tiles/256 filter.eall=HE @cvit batch_size=64 @ start_id=1 @tile sz=256 ovl=64
<a id="file_mode___cvit_uppergi_"></a>
### file_mode       @ cvit/uppergi-->cvataa_wsi
python cvataa/annotate_wsi.py models=cvit wsi_dir=UpperGI-E tiles_dir=UpperGI-Tiles/256 filter.eall=HE @cvit batch_size=1 @ file_mode=1
`nucls_super`
python cvataa/annotate_wsi.py models=cvit wsi_dir=UpperGI-E tiles_dir=UpperGI-Tiles/256 filter.eall=HE @cvit batch_size=5 classifier=nucls_super chunk_size=1e3 @ file_mode=1 end_id=2 start_id=2
`nucls_main`
python cvataa/annotate_wsi.py models=cvit wsi_dir=UpperGI-E tiles_dir=UpperGI-Tiles/256 filter.eall=HE @cvit batch_size=5 classifier=nucls_main chunk_size=1e3 @ file_mode=1 end_id=2 start_id=2

<a id="tnbc___annotate_tasks_"></a>
# tnbc       @ annotate_tasks-->cvat_auto
<a id="clps___tnbc_"></a>
## clps       @ tnbc-->cvataa_wsi
<a id="sam___clps_tnb_c_"></a>
### sam       @ clps/tnbc-->cvataa_wsi
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py models=clps wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE @clps type=sam batch_size=64 @tile sz=8192 ovl=256
<a id="sam2___clps_tnb_c_"></a>
### sam2       @ clps/tnbc-->cvataa_wsi
python cvataa/annotate_wsi.py models=clps wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE @clps type=sam2 batch_size=64 @tile sz=8192 ovl=256
<a id="dino___clps_tnb_c_"></a>
### dino       @ clps/tnbc-->cvataa_wsi
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py models=clps wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE iall=D22 @clps type=dino batch_size=256 @tile sz=8192 ovl=256 max=0
<a id="dino2___clps_tnb_c_"></a>
### dino2       @ clps/tnbc-->cvataa_wsi
python cvataa/annotate_wsi.py models=clps wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE @clps type=dino2 batch_size=64 @tile sz=8192 ovl=256 max=0

<a id="cvit___tnbc_"></a>
## cvit       @ tnbc-->cvataa_wsi
`nucls_super`
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 file_mode=1 @filter iany=D3,D5,D9 eall=HE @cvit batch_size=1 classifier=nucls_super chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 file_mode=1 @filter iall=D5 eall=HE @cvit batch_size=1 classifier=nucls_super chunk_size=0
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 file_mode=1 @filter iall=D9 eall=HE @cvit batch_size=1 classifier=nucls_super chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE eany=D3,D5,D9 @ file_mode=1 start_id=0 @cvit batch_size=2 classifier=nucls_super chunk_size=0
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE @ file_mode=1 start_id=0 @cvit batch_size=2 classifier=nucls_super chunk_size=0
`nucls_main`
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 file_mode=1 @filter iany=D3,D5,D9 eall=HE @cvit batch_size=1 classifier=nucls_main chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE @ file_mode=1 start_id=0 @cvit batch_size=2 classifier=nucls_main chunk_size=0
`ocelot`
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 file_mode=1 @filter iany=D3,D5,D9 eall=HE @cvit batch_size=1 classifier=ocelot chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE @ file_mode=1 start_id=0 @cvit batch_size=2 classifier=ocelot chunk_size=0
`pannuke`
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 file_mode=1 @filter iany=D3,D5,D9 eall=HE @cvit batch_size=1 chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 @filter eall=HE eany=D3,D5,D9 @ file_mode=1 start_id=0 @cvit batch_size=1 chunk_size=0

<a id="tnbc_he___annotate_tasks_"></a>
# tnbc-he       @ annotate_tasks-->cvat_auto
<a id="cellvit___tnbc_h_e_"></a>
## cellvit       @ tnbc-he-->cvataa_wsi
`nucls_super`
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iall=D3_HE file_mode=1 @cvit batch_size=1 classifier=nucls_super chunk_size=0
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iall=D5_HE file_mode=1 @cvit batch_size=2 classifier=nucls_super chunk_size=0
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iall=D9_HE file_mode=1 @cvit batch_size=2 classifier=nucls_super chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 @filter iall=HE eany=D3_HE,D5_HE,D9_HE @ file_mode=1 start_id=13 @cvit batch_size=2 classifier=nucls_super chunk_size=0
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 @filter iall=HE @ file_mode=1 start_id=13 @cvit batch_size=2 classifier=nucls_super chunk_size=0

`nucls_main`
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iall=D3_HE file_mode=1 @cvit batch_size=1 classifier=nucls_main chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iany=D3_HE,D5_HE,D9_HE file_mode=1 @cvit batch_size=4 classifier=nucls_main chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 @filter iall=HE @ file_mode=1 start_id=0 @cvit batch_size=2 classifier=nucls_main chunk_size=0

`ocelot`
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iall=D3_HE file_mode=1 @cvit batch_size=2 classifier=ocelot chunk_size=0
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 @filter iall=_HE eany=D3_HE @ file_mode=1 start_id=0 @cvit batch_size=2 classifier=ocelot chunk_size=0

`pannuke`
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iall=D3_HE file_mode=1 @cvit batch_size=2 chunk_size=0
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iall=D5_HE file_mode=1 @cvit batch_size=5 chunk_size=0
python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 filter.iall=D9_HE file_mode=1 @cvit batch_size=5 chunk_size=0

python cvataa/annotate_wsi.py models=cvit wsi_dir=TNBC-D tiles_dir=TNBC-HandE-Tiles/256 @filter iall=_HE eany=D3_HE,D5_HE,D9_HE @ file_mode=1 start_id=0 @cvit batch_size=2 chunk_size=0


<a id="bcw_oct___annotate_tasks_"></a>
# bcw-oct       @ annotate_tasks-->cvat_auto
<a id="clps_er___bcw_oc_t_"></a>
## clps-er       @ bcw-oct-->cvataa_wsi
<a id="dino___clps_er_bcw_oc_t_"></a>
### dino       @ clps-er/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512
`bcw_oct_48-fail`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-64:ihc:sz-8192:ov-512 filter.iany+=CHS24-008310_ER_1,CHS24-007458_ER_0,CHS24-007401_ER_0,CHS24-006429_ER_3
`bcw_oct_48-pass`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-64:ihc:sz-8192:ov-512 filter.eany+=CHS24-008310_ER_1,CHS24-007458_ER_0,CHS24-007401_ER_0,CHS24-006429_ER_3 filter.iany+=CHS24-006429_ER_3,CHS24-007401_ER_0,CHS24-007458_ER_0,CHS24-008310_ER_1,CIS24-001205_ER_3
`bcw_oct_clpsw_dino_260806`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512,bcw_oct_clpsw_dino_260806
`bcw_oct-round_2`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512,bcw_oct-round_2
<a id="qmlp___dino_clps_er_bcw_oct_"></a>
#### qmlp       @ dino/clps-er/bcw-oct-->cvataa_wsi
python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:er
`bcw_oct-round_2`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:er,bcw_oct-round_2 cls_output_path=/mnt/NAS/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-dino/qmlp-bcw_oct_0_9-er
`bcw_oct-round_2-conf80`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:er:conf80,bcw_oct-round_2
`bcw_oct-round_2-conf50`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:er:conf50,bcw_oct-round_2
`bcw_oct-round_2-conf25`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:er:conf25,bcw_oct-round_2
`bcw_oct-round_2-conf10`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:er:conf10,bcw_oct-round_2

<a id="dino2___clps_er_bcw_oc_t_"></a>
### dino2       @ clps-er/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino2:batch-256:ihc:sz-8192:ov-512 eall+=SH24-006537_ER_0
`bcw_oct_48-fail`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino2:batch-64:ihc:sz-8192:ov-512 filter.iany+=CHS24-008310_ER_1,CHS24-007458_ER_0,CHS24-007401_ER_0,CHS24-006429_ER_3
`bcw_oct_48-pass`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-dino2:batch-64:ihc:sz-8192:ov-512 filter.eany+=CHS24-008310_ER_1,CHS24-007458_ER_0,CHS24-007401_ER_0,CHS24-006429_ER_3 filter.iany+=CHS24-006429_ER_3,CHS24-007401_ER_0,CHS24-007458_ER_0,CHS24-008310_ER_1,CIS24-001205_ER_3
<a id="sam___clps_er_bcw_oc_t_"></a>
### sam       @ clps-er/bcw-oct-->cvataa_wsi
`bcw_oct_48`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-sam:batch-64:ihc:sz-8192:ov-512 filter.iany+=CHS24-008310_ER_1,CHS24-007458_ER_0,CHS24-007401_ER_0,CHS24-006429_ER_3
`bcw_oct_48-pass`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-sam:batch-64:ihc:sz-8192:ov-512 filter.eany+=CHS24-008310_ER_1,CHS24-007458_ER_0,CHS24-007401_ER_0,CHS24-006429_ER_3 filter.iany+=CHS24-006429_ER_3,CHS24-007401_ER_0,CHS24-007458_ER_0,CHS24-008310_ER_1,CIS24-001205_ER_3
<a id="sam2___clps_er_bcw_oc_t_"></a>
### sam2       @ clps-er/bcw-oct-->cvataa_wsi
`bcw_oct_48`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-sam2:batch-64:ihc:sz-8192:ov-512 filter.iany+=CHS24-008310_ER_1,CHS24-007458_ER_0,CHS24-007401_ER_0,CHS24-006429_ER_3
`bcw_oct_48-pass`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:er:clps-sam2:batch-64:ihc:sz-8192:ov-512 filter.eany+=CHS24-008310_ER_1,CHS24-007458_ER_0,CHS24-007401_ER_0,CHS24-006429_ER_3 filter.iany+=CHS24-006429_ER_3,CHS24-007401_ER_0,CHS24-007458_ER_0,CHS24-008310_ER_1,CIS24-001205_ER_3

<a id="clps_pr___bcw_oc_t_"></a>
## clps-pr       @ bcw-oct-->cvataa_wsi
<a id="dino___clps_pr_bcw_oc_t_"></a>
### dino       @ clps-pr/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-256:ihc:sz-8192:ov-512
`bcw_oct_48-fail`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-128:ihc:sz-8192:ov-512 filter.iany+=MIS24-008871_PR_2,FHS24-024704_PR_4,CIS24-001205_PR_2,CHS24-008310_PR_4,CHS24-006429_PR_2
`bcw_oct_48-pass`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-64:ihc:sz-8192:ov-512 filter.eany+=MIS24-008871_PR_2,FHS24-024704_PR_4,CIS24-001205_PR_2,CHS24-008310_PR_4,CHS24-006429_PR_2 filter.iany+=CHS24-006429_PR_2,CHS24-007401_PR_3,CHS24-007458_PR_3,CHS24-008310_PR_4,CIS24-001205_PR_2,FHS24-024704_PR_4,RDS24-016403_PR_0,MIS24-008871_PR_2,FHS24-024290_PR_4
`bcw_oct_clpsw_dino_260806`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-256:ihc:sz-8192:ov-512,bcw_oct_clpsw_dino_260806
`bcw_oct-round_2`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-256:ihc:sz-8192:ov-512,bcw_oct-round_2
<a id="qmlp___dino_clps_pr_bcw_oct_"></a>
#### qmlp       @ dino/clps-pr/bcw-oct-->cvataa_wsi
python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:pr
`dbg`
python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:pr filter.iany+=CIS24-001364
`bcw_oct-round_2`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:pr,bcw_oct-round_2 cls_output_path=/mnt/NAS/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-dino
`bcw_oct-round_2-conf80`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:pr:conf80,bcw_oct-round_2


<a id="dino2___clps_pr_bcw_oc_t_"></a>
### dino2       @ clps-pr/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino2:batch-256:ihc:sz-8192:ov-512
`bcw_oct_48`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino2:batch-128:ihc:sz-8192:ov-512 filter.iany+=MIS24-008871_PR_2,FHS24-024704_PR_4,CIS24-001205_PR_2,CHS24-008310_PR_4,CHS24-006429_PR_2
`bcw_oct_48-pass`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-dino2:batch-64:ihc:sz-8192:ov-512 filter.eany+=MIS24-008871_PR_2,FHS24-024704_PR_4,CIS24-001205_PR_2,CHS24-008310_PR_4,CHS24-006429_PR_2 filter.iany+=CHS24-006429_PR_2,CHS24-007401_PR_3,CHS24-007458_PR_3,CHS24-008310_PR_4,CIS24-001205_PR_2,FHS24-024704_PR_4,RDS24-016403_PR_0,MIS24-008871_PR_2,FHS24-024290_PR_4
<a id="sam___clps_pr_bcw_oc_t_"></a>
### sam       @ clps-pr/bcw-oct-->cvataa_wsi
`bcw_oct_48`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-sam:batch-64:ihc:sz-8192:ov-512 filter.iany+=MIS24-008871_PR_2,FHS24-024704_PR_4,CIS24-001205_PR_2,CHS24-008310_PR_4,CHS24-006429_PR_2
`bcw_oct_48-pass`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-sam:batch-64:ihc:sz-8192:ov-512 filter.eany+=MIS24-008871_PR_2,FHS24-024704_PR_4,CIS24-001205_PR_2,CHS24-008310_PR_4,CHS24-006429_PR_2 filter.iany+=CHS24-006429_PR_2,CHS24-007401_PR_3,CHS24-007458_PR_3,CHS24-008310_PR_4,CIS24-001205_PR_2,FHS24-024704_PR_4,RDS24-016403_PR_0,MIS24-008871_PR_2,FHS24-024290_PR_4
<a id="sam2___clps_pr_bcw_oc_t_"></a>
### sam2       @ clps-pr/bcw-oct-->cvataa_wsi
`bcw_oct_48`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-sam2:batch-64:ihc:sz-8192:ov-512 filter.iany+=MIS24-008871_PR_2,FHS24-024704_PR_4,CIS24-001205_PR_2,CHS24-008310_PR_4,CHS24-006429_PR_2
`bcw_oct_48-pass`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:pr:clps-sam2:batch-64:ihc:sz-8192:ov-512 filter.eany+=MIS24-008871_PR_2,FHS24-024704_PR_4,CIS24-001205_PR_2,CHS24-008310_PR_4,CHS24-006429_PR_2 filter.iany+=CHS24-006429_PR_2,CHS24-007401_PR_3,CHS24-007458_PR_3,CHS24-008310_PR_4,CIS24-001205_PR_2,FHS24-024704_PR_4,RDS24-016403_PR_0,MIS24-008871_PR_2,FHS24-024290_PR_4

<a id="clps_ki67___bcw_oc_t_"></a>
## clps-ki67       @ bcw-oct-->cvataa_wsi
<a id="dino___clps_ki67_bcw_oc_t_"></a>
### dino       @ clps-ki67/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=dino batch_size=64 @tile sz=8192 ovl=512 max=0

CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=KI67 eany=FHS24-023560_KI67,HE @clps type=dino batch_size=256 @tile sz=16384 ovl=512 max=0

CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512 filter.iall=FHS24-022393_KI67_2

CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:ssd:oct:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512 filter.iall=FHS24-022393_KI67_2

`bcw_oct_clpsw_dino_260806`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512,bcw_oct_clpsw_dino_260806
`bcw_oct-round_2`
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:oct:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512,bcw_oct-round_2
<a id="qmlp___dino_clps_ki67_bcw_oct_"></a>
#### qmlp       @ dino/clps-ki67/bcw-oct-->cvataa_wsi
python cvataa/annotate_wsi.py cfg=bcw:oct:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:ki67
`bcw_oct-round_2`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:ki67,bcw_oct-round_2
`bcw_oct-round_2-conf80`
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2,qmlp:ki67:conf80,bcw_oct-round_2 

<a id="dino2___clps_ki67_bcw_oc_t_"></a>
### dino2       @ clps-ki67/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=dino2 batch_size=256 @tile sz=8192 ovl=512

CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=KI67 eany=FHS24-023560_KI67,HE @clps type=dino2 batch_size=256 @tile sz=16384 ovl=512 max=0
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=KI67 eany=FHS24-023560_KI67,HE @clps type=dino2 batch_size=256 @tile sz=16384 ovl=512 max=0

https://fiftyone.gilbertbigras.com/datasets/OCTOBER_2024-Ki67-256-multi-instanseg_stardist_cellpose_cellvit-FHS24-023560_KI67_1-grouped?slice=cellpose

<a id="sam___clps_ki67_bcw_oc_t_"></a>
### sam       @ clps-ki67/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:oct:ki67:clps-sam:batch-64:ihc:sz-8192:ov-512:iall-FHS24-023560_KI67
<a id="sam2___clps_ki67_bcw_oc_t_"></a>
### sam2       @ clps-ki67/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=sam2 batch_size=64 @tile sz=8192 ovl=512

CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=KI67 eany=FHS24-023560_KI67,HE @clps type=sam2 batch_size=64 @tile sz=8192 ovl=512 max=0

<a id="subtype_n___sam2_clps_ki67_bcw_oct_"></a>
#### subtype-n       @ sam2/clps-ki67/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=sam2 subtype=n1 batch_size=256 @tile sz=8192 ovl=512

CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=sam2 subtype=n5 batch_size=256 @tile sz=8192 ovl=512

<a id="subtype_p___sam2_clps_ki67_bcw_oct_"></a>
#### subtype-p       @ sam2/clps-ki67/bcw-oct-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=sam2 subtype=p0 batch_size=128 @tile sz=8192 ovl=512

CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=sam2 subtype=p1 batch_size=128 @tile sz=8192 ovl=512

CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=sam2 subtype=p5 batch_size=128 @tile sz=8192 ovl=512

CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw models=clps wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256/Ki67 @filter iall=FHS24-023560_KI67 eall=HE @clps type=sam2 subtype=p10 batch_size=128 @tile sz=8192 ovl=512 max=0



<a id="cellvit___bcw_oc_t_"></a>
## cellvit       @ bcw-oct-->cvataa_wsi
python cvataa/annotate_wsi.py models=cvit wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256 filter.eall=HE @cvit batch_size=64 @ start_id=0 @tile sz=256 ovl=64

<a id="file_mode___cellvit_bcw_oc_t_"></a>
### file_mode       @ cellvit/bcw-oct-->cvataa_wsi
python cvataa/annotate_wsi.py models=cvit wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256 filter.eall=HE @cvit batch_size=4 @ file_mode=1 end_id=0 start_id=0
`nucls_super`
python cvataa/annotate_wsi.py models=cvit wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256 filter.eall=HE file_mode=1 end_id=0 start_id=0 @cvit batch_size=4 classifier=nucls_super chunk_size=0
`nucls_main`
python cvataa/annotate_wsi.py models=cvit wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256 filter.eall=HE @cvit batch_size=1 classifier=nucls_main @ file_mode=1 end_id=0 start_id=0 

<a id="bcw_all___annotate_tasks_"></a>
# bcw-all       @ annotate_tasks-->cvat_auto
<a id="clps_er___bcw_al_l_"></a>
## clps-er       @ bcw-all-->cvataa_wsi
<a id="dino___clps_er_bcw_al_l_"></a>
### dino       @ clps-er/bcw-all-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:sept:er:clps-dino:batch-256:ihc:sz-8192:ov-512:out_ssd
```
QuPath script "/home/gilbert/cvat_pathology/cvataa/qupath/export_annotations_headless.groovy" --args "/data/BreastCancerWSIs/SEPTEMBER2024-QP" --args "/data/BreastCancerWSIs/SEPTEMBER-2024/September 12 2024/CHS24-006079/CHS24-006079_ER_0.svs" --args "/data/BreastCancerWSIs/SEPTEMBER-2024/September 12 2024/CHS24-006079/annotations/CHS24-006079_ER_0.geojson.gz"
```

CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:first:er:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:june:er:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:july:er:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:nov:er:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:dec:er:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd

47+13+10+88+20+50

<a id="clps_pr___bcw_al_l_"></a>
## clps-pr       @ bcw-all-->cvataa_wsi
<a id="dino___clps_pr_bcw_al_l_"></a>
### dino       @ clps-pr/bcw-all-->cvataa_wsi
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:sept:pr:clps-dino:batch-256:ihc:sz-8192:ov-512:out_ssd

CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:first:pr:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:june:pr:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:july:pr:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:nov:pr:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:dec:pr:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd

46+11+13+87+20+50

<a id="clps_ki67___bcw_al_l_"></a>
## clps-ki67       @ bcw-all-->cvataa_wsi
<a id="dino___clps_ki67_bcw_al_l_"></a>
### dino       @ clps-ki67/bcw-all-->cvataa_wsi
CUDA_VISIBLE_DEVICES=1 python cvataa/annotate_wsi.py cfg=bcw:sept:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512:out_ssd
```
conda env config vars set PATH=$PATH:/opt/qupath/bin
```
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:first:ki67:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:june:ki67:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:july:ki67:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:nov:ki67:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd
CUDA_VISIBLE_DEVICES=0 python cvataa/annotate_wsi.py cfg=bcw:dec:ki67:clps-dino:batch-64:ihc:sz-8192:ov-512:out_ssd

47+16+12+88+20+50



