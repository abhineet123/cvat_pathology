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
334117384_174751
334117385_174951
334117386_175151

mismatch
256117473_094536
256117475_094936
256117476_095136
256117479_094736

<a id="sync_ws_i_"></a>
# sync_wsi
python cvataa/sync_wsi.py cfg=rz9
python cvataa/sync_wsi.py cfg=gbt verbose=1
python cvataa/sync_wsi.py cfg=ws1


<a id="deploy_ws_i_"></a>
# deploy_wsi
<a id="rz9___deploy_wsi_"></a>
## rz9       @ deploy_wsi-->cvataa_deploy
python cvataa/deploy_wsi.py cfg=deploy:rz9:pr:clps-dino:batch-256:ihc:sz-8192:ov-512:load-0:max-5,qmlp:pr
<a id="gbt___deploy_wsi_"></a>
## gbt       @ deploy_wsi-->cvataa_deploy
python cvataa/deploy_wsi.py cfg=deploy:gbt:pr:clps-dino:batch-256:ihc:sz-8192:ov-512:load-2:max-2,qmlp:pr
python cvataa/deploy_wsi.py cfg=deploy:gbt:er:clps-dino:batch-256:ihc:sz-8192:ov-512:load-0:max-2,qmlp:er
python cvataa/deploy_wsi.py cfg=deploy:gbt:ki67:clps-dino:batch-256:ihc:sz-8192:ov-512:load-0:max-5,qmlp:ki67 tile_objs=0 verbose=1
<a id="ws1___deploy_wsi_"></a>
## ws1       @ deploy_wsi-->cvataa_deploy
python cvataa/deploy_wsi.py cfg=deploy:ws1:pr:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-5,qmlp:pr
python cvataa/deploy_wsi.py cfg=deploy:ws1:er:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-5,qmlp:er
python cvataa/deploy_wsi.py cfg=deploy:ws1:ki67:clps-dino:batch-64:ihc:sz-8192:ov-512:load-0:max-0,qmlp:ki67 tile_objs=0 verbose=1 skip_seg=1


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










