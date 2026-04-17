<!-- MarkdownTOC -->

- [install](#install_)
    - [issues       @ install](#issues___instal_l_)
    - [fiftyone       @ install](#fiftyone___instal_l_)
        - [delete       @ fiftyone/install](#delete___fiftyone_install_)
        - [start       @ fiftyone/install](#start___fiftyone_install_)
    - [instanseg       @ install](#instanseg___instal_l_)
    - [stardist       @ install](#stardist___instal_l_)
    - [cellpose       @ install](#cellpose___instal_l_)
    - [microsam       @ install](#microsam___instal_l_)
        - [conda       @ microsam/install](#conda___microsam_install_)
        - [venv       @ microsam/install](#venv___microsam_install_)
    - [cellvit       @ install](#cellvit___instal_l_)
        - [shared       @ cellvit/install](#shared___cellvit_instal_l_)
    - [issues       @ install](#issues___instal_l__1)
- [f2gbt       @ install](#f2gbt___instal_l_)

<!-- /MarkdownTOC -->

<a id="install_"></a>
# install
mkvirtualenv -p python3.10  cvat
pip install cvat-cli paramparse
pip uninstall opencv-python-headless
pip install --upgrade opencv-python

add2virtualenv /home/abhineet/microsam
add2virtualenv /home/abhineet/cellvit

export CVAT_ACCESS_TOKEN="AHxpPZmI.jfchlo1EKTq4PpbqYSRerZq0eMAt69GN"
cvat-cli --server-host http://104.205.236.116 --server-port 8080 task ls
cd cvat-sdk/cvat_sdk/auto_annotation/functions

<a id="issues___instal_l_"></a>
## issues       @ install-->cvataa_setup
`opencv imshow hangs up`
probably some sort of conflict between pencv-python and pencv-python-headless
go to site-packages and remove cv2 and opencv-python folders if pip uninstall does not work


<a id="fiftyone___instal_l_"></a>
## fiftyone       @ install-->cvataa_setup
pip install fiftyone

<a id="delete___fiftyone_install_"></a>
### delete       @ fiftyone/install-->cvataa_setup
python cvataa/visualize_tasks.py delete_mode=1

<a id="start___fiftyone_install_"></a>
### start       @ fiftyone/install-->cvataa_setup
python cvataa/visualize_tasks.py start_app=2 port=5151 address=0.0.0.0 permanent=1 remote=1
python cvataa/visualize_tasks.py start_app=2 port=5152 remote=1
python cvataa/visualize_tasks.py start_app=2 port=5153 remote=1

python cvataa/visualize_tasks.py start_app=2 port=5451 remote=1
python cvataa/visualize_tasks.py start_app=2 port=5451 filter.iall=512,grouped
python cvataa/visualize_tasks.py start_app=2 port=5452 remote=1

<a id="instanseg___instal_l_"></a>
## instanseg       @ install-->cvataa_setup
mkvirtualenv -p python3.10  instanseg
git clone https://github.com/abhineet123/instanseg
cd instanseg
pip install -e ".[full]"

<a id="stardist___instal_l_"></a>
## stardist       @ install-->cvataa_setup
mkvirtualenv -p python3.10  stardist
pip install tensorflow
pip install stardist

<a id="cellpose___instal_l_"></a>
## cellpose       @ install-->cvataa_setup
mkvirtualenv -p python3.10  cellpose
python -m pip install scikit-image numpy==1.26.4
python -m pip install cellpose

<a id="microsam___instal_l_"></a>
## microsam       @ install-->cvataa_setup
git clone https://github.com/abhineet123/microsam_private microsam
cd microsam

<a id="conda___microsam_install_"></a>
### conda       @ microsam/install-->cvataa_setup
https://computational-cell-analytics.github.io/micro-sam/micro_sam.html#from-source
conda env create -f environment.yaml
conda activate microsam_conda
pip install -e .
pip install paramparse tqdm cvat-cli opencv-python

conda env update -n base --file environment.yaml

echo $CONDA_PREFIX

/home/abhineet/miniforge3/envs/microsam_conda/bin/

pip install opencv-python
pip uninstall opencv-python
conda uninstall opencv-python-headless

<a id="venv___microsam_install_"></a>
### venv       @ microsam/install-->cvataa_setup
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

`does not work`
pip install -r requirements-dev.txt


<a id="cellvit___instal_l_"></a>
## cellvit       @ install-->cvataa_setup
mkvirtualenv -p python3.10  cellvit

sudo apt install python3.10-dev
pip install cvat-cli paramparse

python -m pip install -r requirements.txt

`not needed`
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121

`requirements file is annoyingly out-of-date and numpy version mismatches are absolutely everywhere`
pip install cupy-cuda12x

pip install --upgrade timm wandb Numba scipy tensorflow scikit-image pandas torch torchvision torchaudio

pip uninstall opencv-python-headless
pip install --upgrade opencv-python
pip uninstall opencv-python

<a id="shared___cellvit_instal_l_"></a>
### shared       @ cellvit/install-->cvataa_setup
`not recommended`
python -m pip install cellvit
pip install numpy==2.2.6

<a id="issues___instal_l__1"></a>
## issues       @ install-->cvataa_setup
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
apt-get update && apt-get install wget curl
wget "https://fastdl.mongodb.org/linux/mongodb-linux-amd64-ubuntu2404-8.0.4.tgz"
tar -xvzf mongodb-linux-amd64-ubuntu2404-8.2.5.tgz
cd mongodb-linux-aarch64-ubuntu2404-8.0.4/bin
./mongod --version

_install from deb_
https://www.mongodb.com/try/download/community
sudo dpkg -i mongodb-org-server_8.2.5_amd64.deb

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




