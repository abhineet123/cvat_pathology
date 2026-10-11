<!-- MarkdownTOC -->

- [eval](#eva_l_)
    - [clps-bcw_oct_ki67_4500       @ eval](#clps_bcw_oct_ki67_4500___eval_)
    - [clps-bcw_oct_48       @ eval](#clps_bcw_oct_48___eval_)
        - [pass-rnd-5k       @ clps-bcw_oct_48/eval](#pass_rnd_5k___clps_bcw_oct_48_eval_)
        - [fail       @ clps-bcw_oct_48/eval](#fail___clps_bcw_oct_48_eval_)
        - [fail-cvat       @ clps-bcw_oct_48/eval](#fail_cvat___clps_bcw_oct_48_eval_)
    - [clps-bcw_oct_er       @ eval](#clps_bcw_oct_er___eval_)
        - [pass-rnd-5k       @ clps-bcw_oct_er/eval](#pass_rnd_5k___clps_bcw_oct_er_eval_)
            - [cls-rf       @ pass-rnd-5k/clps-bcw_oct_er/eval](#cls_rf___pass_rnd_5k_clps_bcw_oct_er_eval_)
        - [fail-cvat       @ clps-bcw_oct_er/eval](#fail_cvat___clps_bcw_oct_er_eval_)
            - [cls-rf       @ fail-cvat/clps-bcw_oct_er/eval](#cls_rf___fail_cvat_clps_bcw_oct_er_eval_)
    - [clps-bcw_oct_6       @ eval](#clps_bcw_oct_6___eval_)
        - [pass-cvat       @ clps-bcw_oct_6/eval](#pass_cvat___clps_bcw_oct_6_eva_l_)
        - [fail-cvat       @ clps-bcw_oct_6/eval](#fail_cvat___clps_bcw_oct_6_eva_l_)
            - [sam,dino       @ fail-cvat/clps-bcw_oct_6/eval](#sam_dino___fail_cvat_clps_bcw_oct_6_eva_l_)
- [bcw-oct       @ annotate_tasks](#bcw_oct___annotate_tasks_)
    - [clps-ki67       @ bcw-oct](#clps_ki67___bcw_oc_t_)
    - [clps-ki67-grp0       @ bcw-oct](#clps_ki67_grp0___bcw_oc_t_)
- [tnbc       @ annotate_tasks](#tnbc___annotate_tasks_)
    - [clps-rf-grp0       @ tnbc](#clps_rf_grp0___tnbc_)
    - [clps-rf-grp1       @ tnbc](#clps_rf_grp1___tnbc_)
    - [clps-rf-grp2       @ tnbc](#clps_rf_grp2___tnbc_)
- [tnbc-he       @ annotate_tasks](#tnbc_he___annotate_tasks_)
    - [cvit-grp0       @ tnbc-he](#cvit_grp0___tnbc_h_e_)
        - [nucls_main       @ cvit-grp0/tnbc-he](#nucls_main___cvit_grp0_tnbc_h_e_)
    - [cvit-grp1       @ tnbc-he](#cvit_grp1___tnbc_h_e_)
        - [bin       @ cvit-grp1/tnbc-he](#bin___cvit_grp1_tnbc_h_e_)

<!-- /MarkdownTOC -->

<a id="eva_l_"></a>
# eval
<a id="clps_bcw_oct_ki67_4500___eval_"></a>
## clps-bcw_oct_ki67_4500       @ eval-->cvataa_vis_wsi
python cvataa/visualize_eval.py model=cellpose eval_file=bcw_oct_ki67_4500 start_id=0

<a id="clps_bcw_oct_48___eval_"></a>
## clps-bcw_oct_48       @ eval-->cvataa_vis_wsi
python cvataa/visualize_eval.py model=cellpose eval_file=bcw_oct_48 start_id=22
python cvataa/visualize_eval.py model=cellpose eval_file=bcw_oct_48 end_id=1

python cvataa/visualize_eval.py search=6a1157 filter.iall=PR,grouped

<a id="pass_rnd_5k___clps_bcw_oct_48_eval_"></a>
### pass-rnd-5k       @ clps-bcw_oct_48/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:grp-m:pass-bcw_oct_48:5k:rnd:chunk-500:uni suffixes=sam,sam2,dino,dino2
<a id="fail___clps_bcw_oct_48_eval_"></a>
### fail       @ clps-bcw_oct_48/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:grp-m:fail-bcw_oct_48:chunk-0:uni suffixes=sam,sam2,dino,dino2
<a id="fail_cvat___clps_bcw_oct_48_eval_"></a>
### fail-cvat       @ clps-bcw_oct_48/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:fail-bcw_oct_48:chunk-10:uni:cvat suffixes=sam
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:fail-bcw_oct_48:chunk-10:uni:cvat suffixes=sam,dino

<a id="clps_bcw_oct_er___eval_"></a>
## clps-bcw_oct_er       @ eval-->cvataa_vis_wsi
python cvataa/visualize_eval.py model=cellpose eval_file=bcw_oct_er
<a id="pass_rnd_5k___clps_bcw_oct_er_eval_"></a>
### pass-rnd-5k       @ clps-bcw_oct_er/eval-->cvataa_vis_wsi
<a id="cls_rf___pass_rnd_5k_clps_bcw_oct_er_eval_"></a>
#### cls-rf       @ pass-rnd-5k/clps-bcw_oct_er/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:qp:clps:cls-rf:pass-bcw_oct_er:rnd:5k:chunk-100:uni:grp0 suffixes=dino
<a id="fail_cvat___clps_bcw_oct_er_eval_"></a>
### fail-cvat       @ clps-bcw_oct_er/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:fail-bcw_oct_er:chunk-10:uni:cvat suffixes=dino
<a id="cls_rf___fail_cvat_clps_bcw_oct_er_eval_"></a>
#### cls-rf       @ fail-cvat/clps-bcw_oct_er/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:qp:clps:cls-rf:fail-bcw_oct_er:chunk-10:uni:cvat suffixes=dino



<a id="clps_bcw_oct_6___eval_"></a>
## clps-bcw_oct_6       @ eval-->cvataa_vis_wsi
python cvataa/visualize_eval.py model=cellpose eval_file=bcw_oct_6
<a id="pass_cvat___clps_bcw_oct_6_eva_l_"></a>
### pass-cvat       @ clps-bcw_oct_6/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:pass-bcw_oct_6:0_0:chunk-10:mxc-1:uni:cvat suffixes=sam
<a id="fail_cvat___clps_bcw_oct_6_eva_l_"></a>
### fail-cvat       @ clps-bcw_oct_6/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:fail-bcw_oct_6:chunk-10:uni:cvat suffixes=sam
`dbg`
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:fail-bcw_oct_6:3_3:chunk-10:uni:cvat suffixes=sam
<a id="sam_dino___fail_cvat_clps_bcw_oct_6_eva_l_"></a>
#### sam,dino       @ fail-cvat/clps-bcw_oct_6/eval-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:all:seg:clps:fail-bcw_oct_6:chunk-10:uni:cvat suffixes=sam,dino
<a id="cls_rf___fail_cvat_clps_bcw_oct_6_eva_l_"></a>


<a id="bcw_oct___annotate_tasks_"></a>
# bcw-oct       @ annotate_tasks-->cvat_auto
<a id="clps_ki67___bcw_oc_t_"></a>
## clps-ki67       @ bcw-oct-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:ki67:ncls:clps suffixes=sam,sam2,dino,dino2 @filter iall=FHS24-023560_KI67 eall=HE
```
f2gbt /data/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-sam/FHS24-023560_KI67_1
f2gbt /data/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-sam2/FHS24-023560_KI67_1
f2gbt /data/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-dino/FHS24-023560_KI67_1
f2gbt /data/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-dino2/FHS24-023560_KI67_1

/data/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-sam/FHS24-023560_KI67_1/FHS24-023560_KI67_1.geojson.gz
/data/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-sam/FHS24-023560_KI67_1/FHS24-023560_KI67_1_cells.geojson.gz
```
<a id="clps_ki67_grp0___bcw_oc_t_"></a>
## clps-ki67-grp0       @ bcw-oct-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=bcw:oct:ki67:ncls:clps:grp0:mxc1 suffixes=sam,sam2,dino,dino2 @filter iall=FHS24-023560_KI67 eall=HE





<a id="tnbc___annotate_tasks_"></a>
# tnbc       @ annotate_tasks-->cvat_auto
<a id="clps_rf_grp0___tnbc_"></a>
## clps-rf-grp0       @ tnbc-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:ihc:clps:qp:cls-rf:grp0:mxc1:iall-D1:eall-D10 suffixes=sam
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:ihc:clps:qp:cls-rf:grp0:mxc1:iall-D1:eall-D10 suffixes=sam2
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:ihc:clps:qp:cls-rf:grp0:mxc1:iall-D1:eall-D10 suffixes=dino
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:ihc:clps:qp:cls-rf:grp0:mxc1:iall-D1:eall-D10 suffixes=dino2
<a id="clps_rf_grp1___tnbc_"></a>
## clps-rf-grp1       @ tnbc-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:ihc:clps:qp:cls-rf:grp1:mxc1:iall-D1:eall-D10 suffixes=sam,sam2,dino,dino2
<a id="clps_rf_grp2___tnbc_"></a>
## clps-rf-grp2       @ tnbc-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:ihc:clps:qp:cls-rf:grp2:mxc1:iall-D1:eall-D10 suffixes=sam,sam2,dino,dino2
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:ihc:clps:qp:cls-rf:grp2:mxc1:iall-D1:eall-D10 suffixes=dino


<a id="tnbc_he___annotate_tasks_"></a>
# tnbc-he       @ annotate_tasks-->cvat_auto
<a id="cvit_grp0___tnbc_h_e_"></a>
## cvit-grp0       @ tnbc-he-->cvataa_vis_wsi
<a id="nucls_main___cvit_grp0_tnbc_h_e_"></a>
### nucls_main       @ cvit-grp0/tnbc-he-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:he:cvit-sam:grp0:iall-D3_HE:sz-1k:mxc1:rnd suffixes=nucls_main
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:he:cvit-sam:grp0:iall-D3_HE:sz-1k:mxc1:rnd suffixes=nucls_super
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:he:cvit-sam:grp0:iall-D3_HE:sz-1k:mxc1:rnd suffixes=ocelot
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:he:cvit-sam:grp0:iall-D3_HE:sz-1k:mxc1:rnd suffixes=pannuke

<a id="cvit_grp1___tnbc_h_e_"></a>
## cvit-grp1       @ tnbc-he-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:he:cvit:grp1:mxc1:rnd suffixes=nucls_main,nucls_super,ocelot,pannuke filter.iall=D3_HE
<a id="bin___cvit_grp1_tnbc_h_e_"></a>
### bin       @ cvit-grp1/tnbc-he-->cvataa_vis_wsi
python cvataa/visualize_wsi.py cfg=pdl1:tnbc:he:cvit:grp1:bin:map:mxc1:rnd suffixes=nucls_main,nucls_super,ocelot,pannuke filter.iall=D3_HE



