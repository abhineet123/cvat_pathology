<!-- MarkdownTOC -->

- [install](#install_)
    - [ws1       @ install](#ws1___instal_l_)
    - [google_api       @ install](#google_api___instal_l_)
    - [misc       @ install](#misc___instal_l_)
- [sync_wsi](#sync_ws_i_)
- [deploy_wsi](#deploy_ws_i_)
    - [rz9       @ deploy_wsi](#rz9___deploy_wsi_)
    - [gbt       @ deploy_wsi](#gbt___deploy_wsi_)
    - [ws1       @ deploy_wsi](#ws1___deploy_wsi_)
- [import_annotations_headless](#import_annotations_headless_)
    - [qupath_import_test_proj       @ import_annotations_headless](#qupath_import_test_proj___import_annotations_headles_s_)
    - [qupath_test_proj_nas       @ import_annotations_headless](#qupath_test_proj_nas___import_annotations_headles_s_)
    - [qupath_test_proj_ssd       @ import_annotations_headless](#qupath_test_proj_ssd___import_annotations_headles_s_)
- [sync_filenames_headless](#sync_filenames_headless_)

<!-- /MarkdownTOC -->

<a id="install_"></a>
# install
mkvirtualenv -p python3.11  cvat_sync

pip install cvat-cli==2.62 paramparse compress_json tqdm scikit-image
pip install opencv-python

pip install gspread

pip install openslide-python openslide-bin
pip install imagecodecs shapely orjson geopandas geojson openpyxl zarr

<a id="ws1___instal_l_"></a>
## ws1       @ install-->cvataa_deploy
sudo ip route add 198.166.248.195 via 192.168.42.129 dev enx025b393e353b
sudo route del -net 198.166.248.195 gw 192.168.42.166 netmask 255.255.255.255 dev enx025b393e353b

sudo ip route add 198.166.248.195 via 172.29.32.1 dev wlx00c0cab473a5

<a id="google_api___instal_l_"></a>
## google_api       @ install-->cvataa_deploy
python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

<a id="misc___instal_l_"></a>
## misc       @ install-->cvataa_deploy
`dummy scanner names`
no mismatch
334117383_174551
334117384_174748
334117385_174932
334117386_175118

ER is last
256117473_094536
256117475_094942
256117476_095121
256117479_094752

<a id="sync_ws_i_"></a>
# sync_wsi
python cvataa/sync_wsi.py cfg=rz9
python cvataa/sync_wsi.py cfg=gbt verbose=1
python cvataa/sync_wsi.py cfg=ws1 verbose=1

<a id="deploy_ws_i_"></a>
# deploy_wsi
<a id="rz9___deploy_wsi_"></a>
## rz9       @ deploy_wsi-->cvataa_deploy
python cvataa/deploy_wsi.py cfg=deploy:rz9:pr:clps-dino:batch-256:ihc:sz-8192:ov-512:load-0:max-5qmlp:pr
<a id="gbt___deploy_wsi_"></a>
## gbt       @ deploy_wsi-->cvataa_deploy
python cvataa/deploy_wsi.py cfg=deploy:gbt:er:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-0qmlp:er verbose=0
python cvataa/deploy_wsi.py cfg=deploy:gbt:pr:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-0qmlp:pr verbose=0
python cvataa/deploy_wsi.py cfg=deploy:gbt:ki67:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-0qmlp:ki67 verbose=0
<a id="ws1___deploy_wsi_"></a>
## ws1       @ deploy_wsi-->cvataa_deploy
python cvataa/deploy_wsi.py cfg=deploy:ws1:pr:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-5qmlp:pr
python cvataa/deploy_wsi.py cfg=deploy:ws1:er:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-5qmlp:er
python cvataa/deploy_wsi.py cfg=deploy:ws1:ki67:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-0qmlp:ki67 tile_objs=0 verbose=1 skip_seg=1


<a id="import_annotations_headless_"></a>
# import_annotations_headless
<a id="qupath_import_test_proj___import_annotations_headles_s_"></a>
## qupath_import_test_proj       @ import_annotations_headless-->cvataa_deploy
./QuPath script /home/gilbert/cvat_pathology/cvataa/qupath/import_annotations_headless.groovy --args /home/NVME-8TB/qupath_import_test_proj

<a id="qupath_test_proj_nas___import_annotations_headles_s_"></a>
## qupath_test_proj_nas       @ import_annotations_headless-->cvataa_deploy
./QuPath script /home/gilbert/cvat_pathology/cvataa/qupath/import_annotations_headless.groovy --args /mnt/NAS/qupath_test_proj_nas

./QuPath script /home/gilbert/cvat_pathology/cvataa/qupath/import_annotations_headless.groovy --args /mnt/NAS/qupath_test_proj_nas --args ER

<a id="qupath_test_proj_ssd___import_annotations_headles_s_"></a>
## qupath_test_proj_ssd       @ import_annotations_headless-->cvataa_deploy
./QuPath script /home/gilbert/cvat_pathology/cvataa/qupath/import_annotations_headless.groovy --args /home/NVME-8TB/qupath_test_proj_ssd --args ER

./QuPath script /home/gilbert/cvat_pathology/cvataa/qupath/import_annotations_headless.groovy --args /home/NVME-8TB/qupath_test_proj_ssd --args /home/NVME-8TB/CIS24-001389_ER_1.svs

<a id="sync_filenames_headless_"></a>
# sync_filenames_headless
QuPath script /home/gilbert/cvat_pathology/cvataa/qupath/sync_filenames_headless.groovy --args /mnt/NAS/Abhineet/SHARED/2026_08/2026_08_26/MIS26-999993/MIS26-999993-A2/MIS26-999993-A2-QP --args /mnt/NAS/Abhineet/SHARED --args /home/NVME-8TB/Magee_test

QuPath script /home/gilbert/cvat_pathology/cvataa/qupath/sync_filenames_headless.groovy --args /mnt/NAS/Abhineet/SHARED/2026_08/2026_08_26/MIS26-999995/MIS26-999995-QP --args /mnt/NAS/Abhineet/SHARED --args /home/NVME-8TB/Magee_test

QuPath script /home/gilbert/cvat_pathology/cvataa/qupath/sync_filenames_headless.groovy --args /mnt/NAS/Abhineet/SHARED/2026_08/2026_08_26/MIS26-999985/MIS26-999985-QP --args /mnt/NAS/Abhineet/SHARED --args /home/NVME-8TB/Magee_test




