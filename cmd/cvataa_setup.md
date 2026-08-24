<!-- MarkdownTOC -->

- [cvat](#cva_t_)
    - [conda       @ cvat](#conda___cvat_)
    - [issues       @ cvat](#issues___cvat_)
    - [git       @ cvat](#git___cvat_)
- [fiftyone       @ install](#fiftyone___instal_l_)
    - [install       @ fiftyone](#install___fiftyone_)
        - [conda       @ install/fiftyone](#conda___install_fiftyone_)
    - [filter       @ fiftyone](#filter___fiftyone_)
        - [no_chunk       @ filter/fiftyone](#no_chunk___filter_fiftyon_e_)
    - [mongodb       @ fiftyone](#mongodb___fiftyone_)
        - [22.04       @ mongodb/fiftyone](#22_04___mongodb_fiftyone_)
        - [24.04       @ mongodb/fiftyone](#24_04___mongodb_fiftyone_)
    - [start       @ fiftyone](#start___fiftyone_)
        - [gbt       @ start/fiftyone](#gbt___start_fiftyone_)
        - [x99       @ start/fiftyone](#x99___start_fiftyone_)
    - [delete       @ fiftyone](#delete___fiftyone_)
    - [config       @ fiftyone](#config___fiftyone_)
    - [issues       @ fiftyone](#issues___fiftyone_)
        - [a6k       @ issues/fiftyone](#a6k___issues_fiftyon_e_)
- [instanseg       @ install](#instanseg___instal_l_)
- [stardist       @ install](#stardist___instal_l_)
- [cellpose       @ install](#cellpose___instal_l_)
    - [3.10       @ cellpose](#3_10___cellpose_)
    - [3.11       @ cellpose](#3_11___cellpose_)
    - [all       @ cellpose](#all___cellpose_)
    - [conda       @ cellpose](#conda___cellpose_)
    - [a6k       @ cellpose](#a6k___cellpose_)
        - [swap       @ a6k/cellpose](#swap___a6k_cellpose_)
- [cellvit       @ install](#cellvit___instal_l_)
    - [venv       @ cellvit](#venv___cellvi_t_)
        - [intellisense       @ venv/cellvit](#intellisense___venv_cellvit_)
    - [conda       @ cellvit](#conda___cellvi_t_)
    - [all       @ cellvit](#all___cellvi_t_)
    - [shared       @ cellvit](#shared___cellvi_t_)
    - [bugs       @ cellvit](#bugs___cellvi_t_)
- [microsam       @ install](#microsam___instal_l_)
    - [conda       @ microsam](#conda___microsam_)
    - [venv       @ microsam](#venv___microsam_)
- [create_tissue_mask       @ NSCLC](#create_tissue_mask___nscl_c_)
    - [BreastCancerWSIs       @ create_tissue_mask](#breastcancerwsis___create_tissue_mask_)
        - [OCTOBER_2024       @ BreastCancerWSIs/create_tissue_mask](#october_2024___breastcancerwsis_create_tissue_mas_k_)
    - [PDL1       @ create_tissue_mask](#pdl1___create_tissue_mask_)
        - [HNSCC       @ PDL1/create_tissue_mask](#hnscc___pdl1_create_tissue_mas_k_)
        - [NSCLC       @ PDL1/create_tissue_mask](#nsclc___pdl1_create_tissue_mas_k_)
        - [Cervix       @ PDL1/create_tissue_mask](#cervix___pdl1_create_tissue_mas_k_)
        - [TNBC       @ PDL1/create_tissue_mask](#tnbc___pdl1_create_tissue_mas_k_)
        - [UpperGI       @ PDL1/create_tissue_mask](#uppergi___pdl1_create_tissue_mas_k_)
- [f2gbt       @ install](#f2gbt___instal_l_)
- [magee_deployment](#magee_deploymen_t_)

<!-- /MarkdownTOC -->

<a id="cva_t_"></a>
# cvat
mkvirtualenv -p python3.10  cvat
mkvirtualenv -p python3.11  cvat

pip install cvat-cli==2.62 paramparse
pip install compress_json scikit-image
pip install --upgrade cvat-cli

sudo apt-get install openslide-tools

pip install openslide-python openslide-bin
pip install matplotlib
pip install geojson
pip install pandas
pip install gspread
pip install imagecodecs shapely orjson geopandas openpyxl zarr 

pip install wxPython

pip uninstall opencv-python
pip uninstall opencv-python-headless

pip install --upgrade opencv-python
pip install opencv-python

add2virtualenv /home/abhineet/microsam
add2virtualenv /home/abhineet/cellvit

export CVAT_ACCESS_TOKEN="AHxpPZmI.jfchlo1EKTq4PpbqYSRerZq0eMAt69GN"
cvat-cli --server-host http://104.205.236.116 --server-port 8080 task ls
cd cvat-sdk/cvat_sdk/auto_annotation/functions


cd ~/.virtualenvs/cvat/lib/python3.10/site-packages
ln -s ~/cellpose/cellpose ./cellpose
ln -s ~/cellvit/cellvit ./cellvit
ln -s ~/pathopatch/pathopatch ./pathopatch

<a id="conda___cvat_"></a>
## conda       @ cvat-->cvataa_setup
conda create --name cvat python=3.10
conda activate cvat

<a id="issues___cvat_"></a>
## issues       @ cvat-->cvataa_setup
`opencv imshow hangs up`
seems to be some sort of conflict between opencv-python and opencv-python-headless
```
pip uninstall opencv-python-headless
pip uninstall opencv-python
```
go to `site-packages` and remove cv2 and opencv-python folders if pip uninstall does not work

pip install numpy==1.26.4
pip install opencv-python==4.8.0.76

<a id="git___cvat_"></a>
## git       @ cvat-->cvataa_setup
git config user.email "asingh1@ualberta.ca"
git config user.name "abhineet123"

git config --global credential.helper store

<a id="fiftyone___instal_l_"></a>
# fiftyone       @ install-->cvataa_setup
<a id="install___fiftyone_"></a>
## install       @ fiftyone-->cvataa_setup
mkvirtualenv -p python3.10  cvat_vis
workon cvat_vis

pip install fiftyone
pip install cvat-cli==2.62 paramparse compress_json

<a id="conda___install_fiftyone_"></a>
### conda       @ install/fiftyone-->cvataa_setup
conda create --name cvat_vis python=3.10
conda activate cvat_vis
conda deactivate
python -m pip install -e .

<a id="filter___fiftyone_"></a>
## filter       @ fiftyone-->cvataa_setup
`regex to filter datasets`
```
^.*?256.*?grouped.*?$
^.*?ER.*?grouped.*?$
^.*?PR.*?grouped.*?$
^.*?PR.*((?!.*chunk.*).)*$
^.*?Ki67.*?grouped.*?$
^.*?256.*?cellvit_grouped.*?$
```
https://stackoverflow.com/a/2220089
https://www.rexegg.com/regex-quickstart.php
https://regex101.com/

<a id="no_chunk___filter_fiftyon_e_"></a>
### no_chunk       @ filter/fiftyone-->cvataa_setup
^((?!.*chunk.*).)*$

^(?!.*chunk).*-ER-.*$
^(?!.*chunk).*-PR-.*$
^(?!.*chunk).*-ER-.*CHS.*$

^(?!.*(?:chunk|ensemble)).*-ER-.*CHS.*$
^(?!.*(?:chunk|ensemble)).*-ER-.*$
^(?!.*(?:chunk|ensemble)).*-PR-.*$


<a id="mongodb___fiftyone_"></a>
## mongodb       @ fiftyone-->cvataa_setup
https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-ubuntu/

<a id="24_04___mongodb_fiftyone_install_"></a>
sudo apt-get install gnupg curl
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | \
sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
--dearmor

<a id="22_04___mongodb_fiftyone_"></a>
### 22.04       @ mongodb/fiftyone-->cvataa_setup
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
<a id="24_04___mongodb_fiftyone_"></a>
### 24.04       @ mongodb/fiftyone-->cvataa_setup
sudo apt-get install gnupg curl
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list

sudo apt-get update
sudo apt-get install -y mongodb-org


<a id="start___fiftyone_"></a>
## start       @ fiftyone-->cvataa_setup
sudo rm -rf /tmp/mongodb-27017.sock
sudo service mongod start

sudo systemctl daemon-reload
sudo systemctl restart mongo

`vscode debuggger hangup`
"justMyCode": true

<a id="gbt___start_fiftyone_"></a>
### gbt       @ start/fiftyone-->cvataa_setup
python cvataa/visualize_tasks.py start_app=2 port=5151 address=0.0.0.0 permanent=1 remote=1
python cvataa/visualize_tasks.py start_app=2 port=5451 remote=1 permanent=1
python cvataa/visualize_tasks.py start_app=2 port=5452 remote=1
<a id="x99___start_fiftyone_"></a>
### x99       @ start/fiftyone-->cvataa_setup
python cvataa/visualize_tasks.py start_app=2 port=5151 remote=1 permanent=1
python cvataa/visualize_tasks.py start_app=2 port=5152 remote=1 permanent=1
python cvataa/visualize_tasks.py start_app=2 port=5153 remote=1

<a id="delete___fiftyone_"></a>
## delete       @ fiftyone-->cvataa_setup
python cvataa/visualize_tasks.py delete_mode=1
python cvataa/visualize_tasks.py delete_mode=2

python cvataa/visualize_tasks.py delete_mode=1 @filter iall=Cervix
python cvataa/visualize_tasks.py delete_mode=1 @filter iall=TNBC
python cvataa/visualize_tasks.py delete_mode=1 @filter iall=wsi-

<a id="config___fiftyone_"></a>
## config       @ fiftyone-->cvataa_setup
python cvataa/visualize_tasks.py config_db=cellpose @filter iall=cellpose,grouped

python cvataa/visualize_tasks.py config_db=cellpose @filter iall=cellpose,grouped,OCTOBER_2024-PR eall=chunk
python cvataa/visualize_tasks.py config_db=cellpose @filter iall=cellpose,grouped,OCTOBER_2024-ER eall=chunk

python cvataa/visualize_tasks.py config_db=cellpose @filter iall=cellpose,grouped,Cervix
python cvataa/visualize_tasks.py config_db=cellpose @filter iall=cellpose,grouped,Cervix
python cvataa/visualize_tasks.py config_db=cellpose @filter iall=cellpose,grouped,NSCLC
python cvataa/visualize_tasks.py config_db=cellpose @filter iall=cellpose,grouped,UpperGI
python cvataa/visualize_tasks.py config_db=cellpose @filter iall=cellpose,grouped,TNBC

<a id="issues___fiftyone_"></a>
## issues       @ fiftyone-->cvataa_setup
`fiftyone exited with error 100:`
https://stackoverflow.com/a/76944357
ps -ef | grep [m]ongo

`AttributeError: _ARRAY_API not found`
pip install numpy==1.26.4

`MongoDB could not be installed on your system. `
https://github.com/voxel51/fiftyone/issues/4216

_mongodb config_
https://voxel51.com/blog/fiftyone-computer-vision-tips-and-tricks-march-22-2024
https://docs.voxel51.com/installation/troubleshooting.html#troubleshooting-linux-imports

https://docs.voxel51.com/user_guide/config.html#configuring-a-mongodb-connection
mkdir ~/.fiftyone
nano ~/.fiftyone/config.json

{
    "database_uri": "mongodb://localhost:27017"
}

_Connection Strings_
https://www.mongodb.com/docs/manual/reference/connection-string/?deployment-type=self&topology=standalone&connection-string-format=standard
https://stackoverflow.com/questions/62260612/how-to-get-the-mongodb-connection-string

mongod --version
mongodb://localhost:27017
mongodb://myDatabaseUser:D1fficultP%40ssw0rd@mongodb0.example.com:27017/?authSource=admin

_setup_
https://www.mongodb.com/docs/manual/administration/install-community/?operating-system=linux&linux-distribution=red-hat&linux-package=default&search-linux=with-search-linux

`mongod.service: Failed with result 'exit-code'.`
_seems to work_
_apparently needs to be done on each restart_
https://stackoverflow.com/a/65483737
sudo rm -rf /tmp/mongodb-27017.sock
sudo service mongod start

_mongodb does not officially support 24.04 over apt_
`now it does: https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-ubuntu/`
https://github.com/voxel51/fiftyone/issues/4526

_install 22.04 mongodb on 24.04_
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update

`Failed to fetch https://repo.mongodb.org/apt/ubuntu/dists/jammy/mongodb-org/7.0/InRelease Could not handshake: A TLS fatal alert has been received.`

_apparently something to do with either linux mint or more likely the HTTPS proxy_

_try http instead of https_
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
gpg --keyserver keyserver.ubuntu.com --recv-keys 160D26BB1785BA38  
gpg --export --armor 160D26BB1785BA38 | sudo apt-key add - && sudo apt-get update 

sudo apt install -y mongodb-org

_install mongodb 8_
sudo apt-get update && apt-get install wget curl
wget "https://fastdl.mongodb.org/linux/mongodb-linux-amd64-ubuntu2404-8.0.4.tgz"
tar -xvzf mongodb-linux-amd64-ubuntu2404-8.2.5.tgz
cd mongodb-linux-aarch64-ubuntu2404-8.0.4/bin
./mongod --version

_install from deb_
https://www.mongodb.com/try/download/community
sudo dpkg -i mongodb-org-server_8.2.5_amd64.deb

<a id="a6k___issues_fiftyon_e_"></a>
### a6k       @ issues/fiftyone-->cvataa_setup
 mongodb-org-mongos : Depends: libc6 (>= 2.38) but 2.36-9+deb12u13 is to be installed
                      Depends: libcurl4t64 (>= 7.16.2) but it is not installable
                      Depends: libssl3t64 (>= 3.0.0) but it is not installable
 mongodb-org-server : Depends: libc6 (>= 2.38) but 2.36-9+deb12u13 is to be installed
                      Depends: libcurl4t64 (>= 7.16.2) but it is not installable
                      Depends: libssl3t64 (>= 3.0.0) but it is not installable



<a id="instanseg___instal_l_"></a>
# instanseg       @ install-->cvataa_setup
mkvirtualenv -p python3.10  instanseg
git clone https://github.com/abhineet123/instanseg
cd instanseg
pip install -e ".[full]"
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
pip install numpy==1.26.4
pip install opencv-python==4.8.0.76

pip install cvat-cli paramparse

<a id="stardist___instal_l_"></a>
# stardist       @ install-->cvataa_setup
mkvirtualenv -p python3.10  stardist

https://www.tensorflow.org/install/source#tested_build_configurations
pip install tensorflow==2.15.0

pip install stardist
pip install opencv-python==4.8.0.76
pip install numpy==1.26.4
pip install cvat-cli paramparse compress_json orjson

```arrayprint.py", line 1599, in _array_str_implementation
TypeError: '<=' not supported between instances of 'str' and 'int'
```
remove `np.set_printoptions(legacy="1.25")`

<a id="cellpose___instal_l_"></a>
# cellpose       @ install-->cvataa_setup

<a id="3_10___cellpose_"></a>
## 3.10       @ cellpose-->cvataa_setup
mkvirtualenv -p python3.10  cellpose

python -m pip  install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121

git clone https://github.com/abhineet123/cellpose
cd cellpose
pip install -r requirements.txt

`works with 3.11 too`
python -m pip install numpy==1.26.4
python -m pip install opencv-python==4.8.0.76

python -m pip uninstall opencv-python
python -m pip uninstall opencv-python-headless

`works with numpy 2 and doesn't hang on imshow but does have qt error in vscode`
python -m pip install opencv-python==4.11.0.86
python -m pip install opencv-python==4.12.0.88
```
ERROR: Could not find a version that satisfies the requirement opencv-python==4.10 (from versions: 3.4.0.14, 3.4.10.37, 3.4.11.41, 3.4.11.43, 3.4.11.45, 3.4.13.47, 3.4.15.55, 3.4.16.57, 3.4.16.59, 3.4.17.63, 3.4.18.65, 4.3.0.38, 4.4.0.40, 4.4.0.46, 4.5.1.48, 4.5.3.56, 4.5.4.60, 4.5.5.64, 4.6.0.66, 4.7.0.72, 4.8.0.74, 4.8.0.76, 4.8.1.78, 4.9.0.80, 4.10.0.82, 4.10.0.84, 4.11.0.86, 4.12.0.88, 4.13.0.90, 4.13.0.92)
```

```
https://forum.qt.io/topic/119109/using-pyqt5-with-opencv-python-cv2-causes-error-could-not-load-qt-platform-plugin-xcb-even-though-it-was-found/5
https://github.com/NVlabs/instant-ngp/discussions/300
```
Package 'qt5-default' has no installation candidate
sudo apt-get install qt6-default

sudo apt-get install qt6-base-dev qt6-tools-dev
sudo apt-get remove qt6-base-dev qt6-tools-dev

export QT_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt6/plugins

<a id="3_11___cellpose_"></a>
## 3.11       @ cellpose-->cvataa_setup
mkvirtualenv -p python3.11  cellpose311
workon cellpose311

python -m pip  uninstall torch torchvision torchaudio
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130

<a id="all___cellpose_"></a>
## all       @ cellpose-->cvataa_setup
python -m pip install -e .

python -m pip uninstall scikit-image

python -m pip install cvat-cli paramparse compress_json scikit-image orjson 
python -m pip install openslide-python openslide-bin shapely

pip install git+https://github.com/facebookresearch/dinov3

`intellisense`
cd ~/.virtualenvs/cellpose/lib/python3.10/site-packages
cd ~/.virtualenvs/cellpose311/lib/python3.11/site-packages

ln -s ~/cellpose/cellpose ./cellpose

<a id="conda___cellpose_"></a>
## conda       @ cellpose-->cvataa_setup
conda env create -n aks_clps -f environment.yml
conda activate aks_clps

conda env create -n aks_clps310 -f environment310.yml
conda activate aks_clps310

conda env create -n aks_clps311 -f environment311.yml
conda activate aks_clps311

conda env config vars set -n aks_clps311 LD_LIBRARY_PATH=/usr/local/cuda-13.2/targets/x86_64-linux/lib:$LD_LIBRARY_PATH
conda env config vars set -n aks_clps311 PATH=/usr/local/cuda-13.2/bin:$PATH
conda env config vars set -n aks_clps311 XLA_FLAGS=--xla_gpu_cuda_data_dir=/usr/local/cuda-13.2

conda deactivate
python -m pip install -e .

<a id="a6k___cellpose_"></a>
## a6k       @ cellpose-->cvataa_setup
mkdir /mnt/NAS/PDL1-2026-Detections
mkdir /mnt/NAS/BreastCancerWSIs-Detections

mv /data/BreastCancerWSIs-Detections/*  /mnt/NAS/BreastCancerWSIs-Detections/
sudo mkdir /data
sudo chmod -R a+rw /data
cd /data
ln -s /mnt/NAS/PDL1-2026-Detections PDL1-2026-Detections
ln -s /mnt/NAS/PDL1-2026-Tiles PDL1-2026-Tiles
ln -s /mnt/NAS/PDL1-2026 PDL1-2026
ln -s /mnt/NAS/Abhineet/BreastCancerWSIs BreastCancerWSIs
ln -s /mnt/NAS/BreastCancerWSIs-Detections BreastCancerWSIs-Detections

git remote add backup https://github.com/abhineet123/cvat_pathology_private
git checkout --track backup/master
git config --global credential.helper store

<a id="swap___a6k_cellpose_"></a>
### swap       @ a6k/cellpose-->cvataa_setup
dd if=/dev/zero of=/home/gilbert/swapfile.img bs=1024 count=64M
sudo chmod 600 /home/gilbert/swapfile.img
sudo chown 0:0 /home/gilbert/swapfile.img
sudo mkswap /home/gilbert/swapfile.img

sudo nano /etc/fstab
/home/gilbert/swapfile.img swap swap sw 0 0

sudo swapon /home/gilbert/swapfile.img

<a id="cellvit___instal_l_"></a>
# cellvit       @ install-->cvataa_setup
git clone https://github.com/abhineet123/cellvit_pp cellvit
git clone https://github.com/abhineet123/cellvit_pp_private cellvit
git clone https://github.com/abhineet123/PathoPatcher pathopatch
cd cellvit

<a id="venv___cellvi_t_"></a>
## venv       @ cellvit-->cvataa_setup
mkvirtualenv -p python3.10  cellvit
sudo apt install python3.10-dev

python -m pip install --no-deps -r requirements_x99.txt


<a id="intellisense___venv_cellvit_"></a>
### intellisense       @ venv/cellvit-->cvataa_setup
cd ~/.virtualenvs/cellvit/lib/python3.10/site-packages
ln -s ~/cellvit/cellvit ./cellvit
ln -s ~/pathopatch/pathopatch ./pathopatch
`a6k`
cd ~/anaconda3/envs/aks_cvit/lib/python3.10/site-packages
ln -s ~/abhineet/cellvit/cellvit ./cellvit
ln -s ~/abhineet/pathopatch/pathopatch ./pathopatch

<a id="conda___cellvi_t_"></a>
## conda       @ cellvit-->cvataa_setup
conda env create -n aks_cvit -f environment.yaml
conda activate aks_cvit
conda deactivate
conda remove -n aks_cvit --all

`without environment.yaml - not needed`
conda create --name cellvit python=3.10
conda activate cellvit
conda remove -n cellvit --all

<a id="all___cellvi_t_"></a>
## all       @ cellvit-->cvataa_setup
pip install cvat-cli paramparse compress_json

`not needed`
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121

`requirements file is annoyingly out-of-date and numpy version mismatches are absolutely everywhere`
pip install openslide-python openslide-bin
pip uninstall openslide-python openslide-bin

pip install imagecodecs shapely

python -m pip install numpy==2.2.6

python -m pip install numpy==1.26.4
pip index versions cupy-cuda12x
pip install cupy-cuda12x==13.6.0
python -m pip install opencv-python==4.8.0.76

pip install cupy-cuda12x
pip install --upgrade timm wandb Numba scipy tensorflow scikit-image pandas torch torchvision torchaudio

pip uninstall opencv-python-headless
pip install --upgrade opencv-python
pip uninstall opencv-python

`not needed since we use custom pathopatch`
pip install pathopatch
pip uninstall pathopatch

<a id="shared___cellvi_t_"></a>
## shared       @ cellvit-->cvataa_setup
`not recommended`
python -m pip install cellvit
pip install numpy==2.2.6

<a id="bugs___cellvi_t_"></a>
## bugs       @ cellvit-->cvataa_setup
`AttributeError: 'Polygon' object has no attribute 'uid'`
use old version of shapely from requirements.txt
https://github.com/shapely/shapely/issues/640#issuecomment-946011233

pip install Shapely==1.8.5.post1

<a id="microsam___instal_l_"></a>
# microsam       @ install-->cvataa_setup
git clone https://github.com/abhineet123/microsam_private microsam
cd microsam

<a id="conda___microsam_"></a>
## conda       @ microsam-->cvataa_setup
https://computational-cell-analytics.github.io/micro-sam/micro_sam.html#from-source
conda env create -f environment.yaml
conda activate microsam_conda
pip install -e .
pip install paramparse tqdm cvat-cli opencv-python compress_json

conda env update -n base --file environment.yaml

echo $CONDA_PREFIX

/home/abhineet/miniforge3/envs/microsam_conda/bin/

pip install opencv-python
pip uninstall opencv-python
conda uninstall opencv-python-headless

<a id="venv___microsam_"></a>
## venv       @ microsam-->cvataa_setup
`doesn't work because of conda-specific nifty`
mkvirtualenv -p python3.12  microsam_pip
pip install -r requirements.txt

pip uninstall nifty
pip install nifty>=1.2.3
pip install imagecodecs
pip install magicgui
pip install napari
pip install natsort
pip install pooch
pip install pyqt5
pip install elf >=0.7.1
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
pip install segment-anything
pip install tqdm
pip install timm
pip install trackastra
pip install xarray
pip install xxhash
pip install zarr
pip install git+https://github.com/ChaoningZhang/MobileSAM.git
pip install paramparse cvat-cli opencv-python
pip install --upgrade cvat-cli
pip install cvat-cli==2.63.0
pip install compress_json

`does not work`
pip install -r requirements-dev.txt

<a id="create_tissue_mask___nscl_c_"></a>
# create_tissue_mask       @ NSCLC-->cvataa_annotate
<a id="breastcancerwsis___create_tissue_mask_"></a>
## BreastCancerWSIs       @ create_tissue_mask-->cvataa_setup
<a id="october_2024___breastcancerwsis_create_tissue_mas_k_"></a>
### OCTOBER_2024       @ BreastCancerWSIs/create_tissue_mask-->cvataa_setup
python cvataa/create_tissue_mask.py cfg=ctm:BreastCancerWSIs wsi_dir=OCTOBER_2024 tiles_dir=OCTOBER_2024_TILES_256 vis=2 tiles=0 load=0 skip_empty=1 start_id=158 filter.eall="_HE"
f2gbt BreastCancerWSIs/OCTOBER_2024/masks-vis
f2gbt BreastCancerWSIs/OCTOBER_2024/masks
/mnt/NAS/Abhineet/BreastCancerWSIs/OCTOBER_2024/masks-vis
<a id="pdl1___create_tissue_mask_"></a>
## PDL1       @ create_tissue_mask-->cvataa_setup
<a id="hnscc___pdl1_create_tissue_mas_k_"></a>
### HNSCC       @ PDL1/create_tissue_mask-->cvataa_setup
python cvataa/create_tissue_mask.py wsi_dir=HNSCC-A tiles_dir=HNSCC-Tiles/256 vis=2 tiles=1 load=0 skip_empty=1 @filter eall="_HE"

f2gbt PDL1-2026/HNSCC-A/masks-vis
f2gbt PDL1-2026/HNSCC-A/masks
f2gbt PDL1-2026/HNSCC-A/annotations
f2gbt PDL1-2026-Tiles/HNSCC-Tiles/256-masks-vis/A1
<a id="nsclc___pdl1_create_tissue_mas_k_"></a>
### NSCLC       @ PDL1/create_tissue_mask-->cvataa_setup
python cvataa/create_tissue_mask.py wsi_dir=NSCLC-B tiles_dir=NSCLC-Tiles/256 vis=2 tiles=1 load=0 skip_empty=1 @filter eall="_HE" 

f2gbt PDL1-2026/NSCLC-B/B3.svs
f2gbt PDL1-2026-Tiles/NSCLC-Tiles/256/B3

f2gbt PDL1-2026/NSCLC-B/masks-vis
f2gbt PDL1-2026/NSCLC-B/masks
f2gbt PDL1-2026/NSCLC-B/annotations
f2gbt PDL1-2026-Tiles/NSCLC-Tiles/256-masks-vis/B1
<a id="cervix___pdl1_create_tissue_mas_k_"></a>
### Cervix       @ PDL1/create_tissue_mask-->cvataa_setup
python cvataa/create_tissue_mask.py wsi_dir=Cervix-C tiles_dir=Cervix-Tiles/256 vis=2 tiles=1 load=0 skip_empty=1 @filter eall="_HE"

f2gbt PDL1-2026/Cervix-C/masks-vis
f2gbt PDL1-2026/Cervix-C/masks
f2gbt PDL1-2026/Cervix-C/annotations
f2gbt PDL1-2026-Tiles/Cervix-Tiles/256-masks-vis
<a id="tnbc___pdl1_create_tissue_mas_k_"></a>
### TNBC       @ PDL1/create_tissue_mask-->cvataa_setup
python cvataa/create_tissue_mask.py wsi_dir=TNBC-D tiles_dir=TNBC-Tiles/256 vis=2 tiles=1 load=0 skip_empty=1 filter.eall="_HE" start_id=0 end_id=0

f2gbt PDL1-2026/TNBC-D/D5.svs
f2gbt PDL1-2026/TNBC-D/D3.svs
f2gbt PDL1-2026/TNBC-D/D9.svs

f2gbt PDL1-2026/TNBC-D/D5_HE.svs
f2gbt PDL1-2026/TNBC-D/D3_HE.svs
f2gbt PDL1-2026/TNBC-D/D9_HE.svs

f2gbt PDL1-2026-Tiles/TNBC-Tiles/256/D5
f2gbt PDL1-2026-Tiles/TNBC-Tiles/256/D3
f2gbt PDL1-2026-Tiles/TNBC-Tiles/256/D9

f2gbt PDL1-2026-Tiles/TNBC-HandE-Tiles/256/D5_HE
f2gbt PDL1-2026-Tiles/TNBC-HandE-Tiles/256/D3_HE
f2gbt PDL1-2026-Tiles/TNBC-HandE-Tiles/256/D9_HE

f2gbt PDL1-2026/TNBC-D/masks-vis
f2gbt PDL1-2026/TNBC-D/masks
f2gbt PDL1-2026/TNBC-D/annotations
f2gbt PDL1-2026-Tiles/TNBC-Tiles/256-masks-vis/D1
<a id="uppergi___pdl1_create_tissue_mas_k_"></a>
### UpperGI       @ PDL1/create_tissue_mask-->cvataa_setup
python cvataa/create_tissue_mask.py wsi_dir=UpperGI-E tiles_dir=UpperGI-Tiles/256 vis=2 tiles=0 @filter eall="_HE"

f2gbt PDL1-2026/UpperGI-E/E7.svs
f2gbt PDL1-2026-Tiles/UpperGI-Tiles/256/E7

f2gbt PDL1-2026/UpperGI-E/masks-vis
f2gbt PDL1-2026/UpperGI-E/masks
f2gbt PDL1-2026/UpperGI-E/annotations
f2gbt PDL1-2026-Tiles/UpperGI-Tiles/256-masks-vis/E1


<a id="f2gbt___instal_l_"></a>
# f2gbt       @ install-->cvat_auto_setup
f2gbt /data/PDL1-2026-Tiles/TNBC-HandE-Tiles/256/D10_HE
f2gbt /data/PDL1-2026-Tiles/TNBC-HandE-Tiles/512/D10_HE
f2gbt /data/PDL1-2026-Tiles/TNBC-HandE-Tiles/1024/D10_HE

f2gbt /data/PDL1-2026-Tiles/TNBC-Tiles/256/D10
f2gbt /data/PDL1-2026-Tiles/TNBC-Tiles/512/D10
f2gbt /data/PDL1-2026-Tiles/TNBC-Tiles/1024/D10

f2gbt /data/PDL1-2026/TNBC-D/D10.svs
f2gbt /data/PDL1-2026/TNBC-D/D10_HE.svs

<a id="magee_deploymen_t_"></a>
# magee_deployment
 ln -s /mnt/NAS/Abhineet/BreastCancerWSIs/OCTOBER_2024/CHS24-006429_ER_3.svs /home/gilbert/magee_deployment/260903/260903-patient_1/260903-patient_1-ER.svs
 ln -s /mnt/NAS/Abhineet/BreastCancerWSIs/OCTOBER_2024/CHS24-006429_PR_2.svs /home/gilbert/magee_deployment/260903/260903-patient_1/260903-patient_1-PR.svs
 ln -s /mnt/NAS/Abhineet/BreastCancerWSIs/OCTOBER_2024/CHS24-006429_KI67_4.svs /home/gilbert/magee_deployment/260903/260903-patient_1/260903-patient_1-Ki67.svs
 ln -s /mnt/NAS/Abhineet/BreastCancerWSIs/OCTOBER_2024/CHS24-006429_KI67_4.svs /home/gilbert/magee_deployment/260903/260903-patient_1/260903-patient_1-HE.svs


