<!-- MarkdownTOC -->

- [git](#git_)
- [startup issues](#startup_issues_)
  - [nuclio       @ startup_issues](#nuclio___startup_issues_)
  - [fiftyone       @ startup_issues](#fiftyone___startup_issues_)
  - [cuda       @ startup_issues](#cuda___startup_issues_)
- [install](#install_)
  - [docker       @ install](#docker___instal_l_)
  - [nvidia       @ install](#nvidia___instal_l_)
  - [cvat       @ install](#cvat___instal_l_)
    - [no_auto_start       @ cvat/install](#no_auto_start___cvat_install_)
    - [list       @ cvat/install](#list___cvat_install_)
    - [logs       @ cvat/install](#logs___cvat_install_)
    - [admin_user       @ cvat/install](#admin_user___cvat_install_)
    - [nuctl       @ cvat/install](#nuctl___cvat_install_)
- [deploy       @ serverless/cvat/install](#deploy___serverless_cvat_instal_l_)
  - [x99       @ deploy](#x99___deploy_)
    - [serverless       @ x99/deploy](#serverless___x99_deploy_)
  - [gbt       @ deploy](#gbt___deploy_)
    - [volumes       @ gbt/deploy](#volumes___gbt_deploy_)
      - [cvat_volumes       @ volumes/gbt/deploy](#cvat_volumes___volumes_gbt_deploy_)
    - [cli       @ gbt/deploy](#cli___gbt_deploy_)
    - [https       @ gbt/deploy](#https___gbt_deploy_)
      - [issues       @ https/gbt/deploy](#issues___https_gbt_deploy_)
  - [down       @ deploy](#down___deploy_)
    - [nuclio_wrapper       @ down/deploy](#nuclio_wrapper___down_deplo_y_)
  - [functions       @ deploy](#functions___deploy_)
    - [microsam       @ functions/deploy](#microsam___functions_deploy_)
      - [hp       @ microsam/functions/deploy](#hp___microsam_functions_deplo_y_)
      - [lm       @ microsam/functions/deploy](#lm___microsam_functions_deplo_y_)
      - [mi       @ microsam/functions/deploy](#mi___microsam_functions_deplo_y_)
      - [dbg       @ microsam/functions/deploy](#dbg___microsam_functions_deplo_y_)
    - [instanseg       @ functions/deploy](#instanseg___functions_deploy_)
      - [debug       @ instanseg/functions/deploy](#debug___instanseg_functions_deploy_)
    - [stardist       @ functions/deploy](#stardist___functions_deploy_)
    - [cellpose       @ functions/deploy](#cellpose___functions_deploy_)
    - [cellvit       @ functions/deploy](#cellvit___functions_deploy_)
      - [sam       @ cellvit/functions/deploy](#sam___cellvit_functions_deploy_)
      - [hipt       @ cellvit/functions/deploy](#hipt___cellvit_functions_deploy_)
      - [virchow       @ cellvit/functions/deploy](#virchow___cellvit_functions_deploy_)
    - [openvino       @ functions/deploy](#openvino___functions_deploy_)
    - [iog       @ functions/deploy](#iog___functions_deploy_)
    - [sam       @ functions/deploy](#sam___functions_deploy_)
    - [retinanet_r101       @ functions/deploy](#retinanet_r101___functions_deploy_)
    - [manage       @ functions/deploy](#manage___functions_deploy_)
    - [debug       @ functions/deploy](#debug___functions_deploy_)
      - [vscode       @ debug/functions/deploy](#vscode___debug_functions_deploy_)
- [data](#dat_a_)
- [move](#mov_e_)
  - [docker       @ move](#docker___move_)
  - [containerd       @ move](#containerd___move_)
- [prune       @ docker/free_space](#prune___docker_free_spac_e_)

<!-- /MarkdownTOC -->

<a id="git_"></a>
# git
git remote add official https://github.com/cvat-ai/cvat
git.exe remote add official https://github.com/cvat-ai/cvat
git.exe fetch --all
 
git.exe merge official/master --allow-unrelated-histories

git.exe checkout -b merged master
git.exe checkout master

git.exe rebase -X theirs official/master

git diff master origin/master
git push origin master --force

<a id="startup_issues_"></a>
# startup issues
<a id="nuclio___startup_issues_"></a>
## nuclio       @ startup_issues-->cvat_setup
`Detection error occurred Request failed with status code 503`
https://github.com/cvat-ai/cvat/issues/6582#issuecomment-1732266118
add custom port to each function.yaml

<a id="fiftyone___startup_issues_"></a>
## fiftyone       @ startup_issues-->cvat_setup
`pymongo.errors.ServerSelectionTimeoutError`
https://stackoverflow.com/a/65483737
sudo rm -rf /tmp/mongodb-27017.sock
sudo service mongod start

<a id="cuda___startup_issues_"></a>
## cuda       @ startup_issues-->cvat_setup
`UserWarning: CUDA is not available or torch_xla is imported`
reinstall nvidia container toolkit

<a id="install_"></a>
# install
https://docs.cvat.ai/docs/administration/community/basics/installation/

<a id="docker___instal_l_"></a>
## docker       @ install-->cvat_setup
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo groupadd docker
sudo usermod -aG docker abhineet
sudo usermod -aG docker gilbert

/var/lib/containerd


<a id="nvidia___instal_l_"></a>
## nvidia       @ install-->cvat_setup
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

sudo apt-get update && sudo apt-get install -y --no-install-recommends curl gnupg2

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update

export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.18.2-1
sudo apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}

sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi

<a id="cvat___instal_l_"></a>
## cvat       @ install-->cvat_setup
git clone https://github.com/cvat-ai/cvat
cd cvat

docker compose up -d
docker compose down

sudo docker compose up -d
sudo docker compose down

<a id="no_auto_start___cvat_install_"></a>
### no_auto_start       @ cvat/install-->cvat_setup
docker update --restart=no my-container

<a id="list___cvat_install_"></a>
### list       @ cvat/install-->cvat_setup
docker ps -a

https://stackoverflow.com/a/77437361
docker compose ps --format "{{.Service}} {{.State}}"
docker compose ps --services --status=running

<a id="logs___cvat_install_"></a>
### logs       @ cvat/install-->cvat_setup
sudo docker logs cvat_ui -f
sudo docker logs cvat_server -f
sudo docker logs nuclio -f
sudo docker logs cvat.pth.instanseg:latest-gpu -f

sudo docker inspect --format '{{ index .Config.Labels "traefik.http.routers.cvat.rule"}}' cvat_server

curl -Lv 104.205.236.116:8080

<a id="admin_user___cvat_install_"></a>
### admin_user       @ cvat/install-->cvat_setup
docker exec -it cvat_server bash -ic 'python3 ~/manage.py createsuperuser'

<a id="nuctl___cvat_install_"></a>
### nuctl       @ cvat/install-->cvat_setup
https://docs.cvat.ai/docs/administration/community/advanced/installation_automatic_annotation/

wget https://github.com/nuclio/nuclio/releases/download/1.15.9/nuctl-1.15.9-linux-amd64

sudo chmod +x nuctl-1.15.9-linux-amd64
sudo ln -sf $(pwd)/nuctl-1.15.9-linux-amd64 /usr/local/bin/nuctl

<a id="deploy___serverless_cvat_instal_l_"></a>
# deploy       @ serverless/cvat/install-->cvat_setup
<a id="x99___deploy_"></a>
## x99       @ deploy-->cvat_setup
http://localhost:8080/
http://104.205.236.116:8080/

export CVAT_HOST=104.205.236.116

export CVAT_HOST=localhost:8080
export CVAT_HOST=localhost:8070

CVAT_HOST=104.205.236.116 docker compose up -d

CVAT_HOST=104.205.236.116 sudo -E docker compose up -d


<a id="serverless___x99_deploy_"></a>
### serverless       @ x99/deploy-->cvat_setup
CVAT_HOST=104.205.236.116 docker compose -f docker-compose.yml -f components/serverless/docker-compose.serverless.yml up -d

docker compose down

<a id="gbt___deploy_"></a>
## gbt       @ deploy-->cvat_setup
CVAT_HOST=cvat.gilbertbigras.com docker compose -f docker-compose.yml -f docker-compose.gbt.yml -f components/serverless/docker-compose.serverless.yml up -d

<a id="volumes___gbt_deploy_"></a>
### volumes       @ gbt/deploy-->cvat_setup
<a id="cvat_volumes___volumes_gbt_deploy_"></a>
#### cvat_volumes       @ volumes/gbt/deploy-->cvat_setup
https://github.com/cvat-ai/cvat/issues/5463#issuecomment-1351259923
docker inspect cvat_cvat_data
docker inspect cvat_cvat_db
```
volumes:
  cvat_data:
    name: cvat_cvat_data
    driver_opts:
      device: /home/NVME-8TB/cvat_data
      o: bind
      type: none
  cvat_db:
    name: cvat_cvat_db
    driver_opts:
      device: /home/NVME-8TB/cvat_db
      o: bind
      type: none
```


<a id="cli___gbt_deploy_"></a>
### cli       @ gbt/deploy-->cvat_setup
docker compose -f docker-compose.yml up -d

http://localhost:8080/
https://cvat.gilbertbigras.com
https://cvat.gilbertbigras.com/api/v1/auth/logout
https://cvat.gilbertbigras.com/auth/login

export CVAT_HOST=cvat.gilbertbigras.com

CVAT_HOST=cvat.gilbertbigras.com docker compose up -d
CVAT_HOST=cvat.gilbertbigras.com sudo -E docker compose up -d

docker compose down

<a id="https___gbt_deploy_"></a>
### https       @ gbt/deploy-->cvat_setup
https://docs.cvat.ai/docs/administration/community/basics/installation/#deploy-secure-cvat-instance-with-https

`this seems to be only meant for using the https server provided by Let’s Encrypt`
CVAT_HOST=cvat.gilbertbigras.com docker compose -f docker-compose.yml -f docker-compose.https.yml up -d

<a id="issues___https_gbt_deploy_"></a>
#### issues       @ https/gbt/deploy-->cvat_setup
`Origin checking failed`
`CSRF_TRUSTED_ORIGINS`

https://github.com/cvat-ai/cvat/issues/6321
https://github.com/cvat-ai/cvat/issues/7382
https://github.com/cvat-ai/cvat/issues/8782

https://github.com/cvat-ai/cvat/pull/6322
https://github.com/cvat-ai/cvat/pull/7313

working solution:
https://github.com/cvat-ai/cvat/pull/6322#issuecomment-2257131513

Create a `local-settings.py` file that will be used to overlay the standard production settings.
Contents:
```
# Overlaying production
from cvat.settings.production import *

CSRF_TRUSTED_ORIGINS = ['https://cvat.gilbertbigras.com']
```

Then create a file for docker-compose to apply the settings named  `docker-compose.settings_overlay.local.yml`
Contents:
```
services:
  cvat_server:
    environment:
      DJANGO_SETTINGS_MODULE: settings
    volumes:
      - ./local-settings.py:/home/django/settings.py:ro
```

docker compose -f docker-compose.yml -f docker-compose.settings_overlay.local.yml up -d
docker compose down

<a id="down___deploy_"></a>
## down       @ deploy-->cvat_setup
docker compose down

`Network cvat_cvat Resource is still in use ` 
docker network inspect cvat_cvat

docker network disconnect -f cvat_cvat nuclio-nuclio-pth-facebookresearch-detectron2-retinanet-r101
docker network disconnect -f cvat_cvat nuclio-nuclio-pth-facebookresearch-sam-vit-h
docker network disconnect -f cvat_cvat nuclio-nuclio-openvino-omz-public-mask-rcnn-inception-resnet-v2-atrous-coco
docker network disconnect -f cvat_cvat nuclio-nuclio-pth-shiyinzhang-iog

docker network disconnect -f cvat_cvat nuclio-nuclio-pth-instanSeg
docker network disconnect -f cvat_cvat nuclio-nuclio-pth-stardist
docker network disconnect -f cvat_cvat nuclio-nuclio-pth-cellpose
docker network disconnect -f cvat_cvat nuclio-nuclio-pth-cellvit-sam
docker network disconnect -f cvat_cvat nuclio-nuclio-pth-cellvit-hipt
docker network disconnect -f cvat_cvat nuclio-nuclio-pth-cellvit-virchow

docker network disconnect -f cvat_cvat nuclio

<a id="nuclio_wrapper___down_deplo_y_"></a>
### nuclio_wrapper       @ down/deploy-->cvat_setup
ps -p 2268310 -o pid,vsz=MEMORY -o user,group=GROUP -o comm,args=ARGS

<a id="functions___deploy_"></a>
## functions       @ deploy-->cvat_setup
chmod +x ./serverless/deploy_cpu.sh
chmod +x ./serverless/deploy_gpu.sh

nuctl get function --platform local

nuctl delete function pth-instanSeg --platform local --force
nuctl delete function pth-stardist --platform local --force
nuctl delete function pth-cellpose --platform local --force
nuctl delete function pth-cellvit-sam --platform local --force
nuctl delete function pth-cellvit-hipt --platform local --force
nuctl delete function pth-cellvit-virchow --platform local --force

nuctl delete function pth-microsam --platform local --force

nuctl delete function pth-facebookresearch-sam-vit-h --platform local --force
nuctl delete function pth-facebookresearch-detectron2-retinanet-r101 --platform local

<a id="microsam___functions_deploy_"></a>
### microsam       @ functions/deploy-->cvat_setup
docker system prune -a

sudo chown -R abhineet: /data/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/5343
watch sudo cat /data/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/5343/fs/opt/nuclio/microsam/nuctl_outputs.log
sudo ls /data/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/5283/fs/opt/nuclio/microsam/nuctl_outputs.log

./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam
docker logs nuclio-nuclio-pth-microsam -f
nuctl delete function pth-microsam --platform local --force

docker exec -it nuclio-nuclio-pth-microsam /bin/bash
ssh-keygen -q -t rsa -N '' -C "microsam" -f /root/.ssh/id_rsa
cat /root/.ssh/id_rsa.pub
apt update && apt install ssh nano
nano /root/.ssh/config
ssh -R 5679:localhost:5679 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null x99

<a id="hp___microsam_functions_deplo_y_"></a>
#### hp       @ microsam/functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_hp_huge
docker logs nuclio-nuclio-pth-microsam_hp_huge -f
nuctl delete function pth-microsam_hp_huge --platform local --force

./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_hp_base
docker logs nuclio-nuclio-pth-microsam_hp_base -f
nuctl delete function pth-microsam_hp_base --platform local --force

<a id="lm___microsam_functions_deplo_y_"></a>
#### lm       @ microsam/functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_lm_large
docker logs nuclio-nuclio-pth-microsam_lm_large -f
nuctl delete function pth-microsam_lm_large --platform local --force

<a id="mi___microsam_functions_deplo_y_"></a>
#### mi       @ microsam/functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_mi_base
docker logs nuclio-nuclio-pth-microsam_mi_base -f
nuctl delete function pth-microsam_mi_base --platform local --force



<a id="dbg___microsam_functions_deplo_y_"></a>
#### dbg       @ microsam/functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_dummy

./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam311
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam310

nuctl delete function pth-microsam310 --platform local --force
nuctl delete function pth-microsam311 --platform local --force

<a id="instanseg___functions_deploy_"></a>
### instanseg       @ functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/instanseg instanseg
docker logs nuclio-nuclio-pth-instanSeg -f
<a id="debug___instanseg_functions_deploy_"></a>
#### debug       @ instanseg/functions/deploy-->cvat_setup
docker exec -it nuclio-nuclio-pth-instanSeg /bin/bash
cat /root/.ssh/id_rsa.pub
ssh -R 5678:localhost:5678 x99

<a id="stardist___functions_deploy_"></a>
### stardist       @ functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/stardist stardist
docker logs nuclio-nuclio-pth-stardist -f

<a id="cellpose___functions_deploy_"></a>
### cellpose       @ functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/cellpose cellpose
docker logs nuclio-nuclio-pth-cellpose -f

<a id="cellvit___functions_deploy_"></a>
### cellvit       @ functions/deploy-->cvat_setup
<a id="sam___cellvit_functions_deploy_"></a>
#### sam       @ cellvit/functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/cellvit cellvit
docker logs nuclio-nuclio-pth-cellvit-sam -f

<a id="hipt___cellvit_functions_deploy_"></a>
#### hipt       @ cellvit/functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/cellvit cellvit-hipt
docker logs nuclio-nuclio-pth-cellvit-hipt -f

<a id="virchow___cellvit_functions_deploy_"></a>
#### virchow       @ cellvit/functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/cellvit cellvit-virchow
docker logs nuclio-nuclio-pth-cellvit-virchow -f

<a id="openvino___functions_deploy_"></a>
### openvino       @ functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/openvino/dextr
./serverless/deploy_gpu.sh serverless/openvino/omz/public/yolo-v3-tf

./serverless/deploy_cpu.sh serverless/openvino/dextrpublic
./serverless/deploy_cpu.sh serverless/openvino/omz//yolo-v3-tf
./serverless/deploy_cpu.sh serverless/openvino/omz/public/mask_rcnn_inception_resnet_v2_atrous_coco

<a id="iog___functions_deploy_"></a>
### iog       @ functions/deploy-->cvat_setup
./serverless/deploy_cpu.sh serverless/pytorch/shiyinzhang/iog
<a id="sam___functions_deploy_"></a>
### sam       @ functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/facebookresearch/sam
<a id="retinanet_r101___functions_deploy_"></a>
### retinanet_r101       @ functions/deploy-->cvat_setup
./serverless/deploy_gpu.sh serverless/pytorch/facebookresearch/detectron2/retinanet_r101

<a id="manage___functions_deploy_"></a>
### manage       @ functions/deploy-->cvat_setup
nuctl get function --platform local

nuctl delete function pth-instanSeg --platform local
nuctl delete function pth-cellvit --platform local --force
nuctl delete function pth-stardist --platform local --force

nuctl deploy --project-name cvat --path "serverless/pytorch/instanseg/nuclio" \
    --file "serverless/pytorch/instanseg/nuclio/function-gpu.yaml" --platform local \
    --env CVAT_FUNCTIONS_REDIS_HOST=cvat_redis_ondisk \
    --env CVAT_FUNCTIONS_REDIS_PORT=6666 \
    --platform-config '{"attributes": {"network": "cvat_cvat"}}'

nuctl deploy --project-name cvat \
  --path serverless/tensorflow/matterport/mask_rcnn/nuclio \
  --platform local --base-image tensorflow/tensorflow:1.15.5-gpu-py3 \
  --desc "GPU based implementation of Mask RCNN on Python 3, Keras, and TensorFlow." \
  --image cvat/tf.matterport.mask_rcnn_gpu \
  --triggers '{"myHttpTrigger": {"maxWorkers": 1}}' \
  --resource-limit nvidia.com/gpu=1

<a id="debug___functions_deploy_"></a>
### debug       @ functions/deploy-->cvat_setup
docker logs cvat_server -f
docker logs nuclio -f

docker logs nuclio-nuclio-pth-instanSeg -f
docker logs nuclio-nuclio-pth-cellvit -f
docker logs nuclio-nuclio-pth-cellpose -f
docker logs nuclio-nuclio-pth-stardist -f

docker logs nuclio-nuclio-pth-microsam -f

`Error: Could not get models from the server`
`ERROR django.request: Internal Server Error: /api/lambda/functions`
`json.decoder.JSONDecodeError: Expecting value: line 3 column 1 (char 52)`
https://github.com/cvat-ai/cvat/issues/6346#issuecomment-1600484678
fix errors in nuclio functions.yaml files

`OPAHealthCheck Internal Server Error for url: http://opa:8181/health?bundles`
https://github.com/cvat-ai/cvat/issues/8451#issuecomment-2375267178
doesn't seem to prevent cvat from running normally

<a id="vscode___debug_functions_deploy_"></a>
#### vscode       @ debug/functions/deploy-->cvat_setup
https://docs.cvat.ai/docs/guides/serverless-tutorial/#debugging-a-serverless-function

docker exec -it nuclio-nuclio-pth-microsam /bin/bash
cat /root/.ssh/id_rsa.pub


<a id="dat_a_"></a>
# data
https://github.com/cvat-ai/cvat/issues/4675#issuecomment-1148547464
/var/lib/docker/volumes/cvat_cvat_data/_data/data
/var/lib/docker/volumes/cvat_cvat_data/_data/projects
/var/lib/docker/volumes/cvat_cvat_data/_data/tasks
/var/lib/docker/volumes/cvat_cvat_data/_data/cache
raw images for a project
/var/lib/docker/volumes/cvat_cvat_data/_data/data/48/raw

<a id="mov_e_"></a>
# move

<a id="docker___move_"></a>
## docker       @ move-->cvat_setup
https://stackoverflow.com/questions/59345566/move-docker-volume-to-different-partition
sudo service docker stop  

`Stopping 'docker.service', but its triggering units are still active`
https://stackoverflow.com/questions/47489631/warning-stopping-docker-service-but-it-can-still-be-activated-by-docker-socke
sudo systemctl stop docker.socket

mkdir /home/NVME-8TB/docker
mkdir /data/docker

sudo gedit /etc/docker/daemon.json
sudo nano /etc/docker/daemon.json

```
"data-root": "/home/NVME-8TB/docker",
```
```
"data-root": "/data/docker",
```
```
{
    "data-root": "/data/docker",
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```
sudo rsync -aP /var/lib/docker/ /home/NVME-8TB/docker
sudo rsync -aP /var/lib/docker/ /data/docker

sudo mv /var/lib/docker /var/lib/docker.old

sudo ln -s /home/NVME-8TB/docker /var/lib/docker
sudo ln -s /data/docker /var/lib/docker

sudo service docker start
docker run --rm hello-world
sudo rm -rf /var/lib/docker.old

<a id="containerd___move_"></a>
## containerd       @ move-->cvat_setup
https://stackoverflow.com/a/73330152

sudo service containerd stop

sudo nano /etc/containerd/config.toml
```
root = "/data/containerd"
```

mkdir /home/NVME-8TB/containerd
mkdir /data/containerd

sudo rsync -aP /var/lib/containerd/ /home/NVME-8TB/containerd
sudo rsync -aP /var/lib/containerd/ /data/containerd

sudo rm -rf /var/lib/containerd

sudo ln -s /home/NVME-8TB/containerd /var/lib/containerd
sudo ln -s /data/containerd /var/lib/containerd

sudo service containerd start

<a id="prune___docker_free_spac_e_"></a>
# prune       @ docker/free_space-->cvat_setup
https://forums.docker.com/t/how-to-delete-cache/5753

`seems to work – Total reclaimed space: 506.8GB`
docker system prune -a

`doesn't seem to do much`
alias docker_clean_images='docker rmi $(docker images -a --filter=dangling=true -q)'
alias docker_clean_ps='docker rm $(docker ps --filter=status=exited --filter=status=created -q)'
docker_clean_images
docker_clean_ps

`doesn't seem to do much`
docker builder prune

`apparently works somewhat but not for snapshots`
https://docs.docker.com/engine/manage-resources/pruning/

https://docs.docker.com/reference/cli/docker/image/prune/
docker image prune -a

https://docs.docker.com/reference/cli/docker/container/prune/
docker container ls
docker ps --size
docker container prune

https://docs.docker.com/reference/cli/docker/volume/prune/
docker volume ls
docker volume prune


`too much work to install`
https://stackoverflow.com/a/73273842

nerdctl is a Docker-compatible CLI for containerd.
https://github.com/containerd/nerdctl

nerdctl system prune --all

`works better but not quite to actually prune anything`
https://hexshift.medium.com/how-to-cleanly-remove-images-containers-and-snapshots-in-containerd-c477d4d7fd58
sudo ctr namespaces list

sudo ctr --namespace moby containers list
sudo ctr --namespace moby_history containers list

sudo ctr --namespace default images list
sudo ctr --namespace moby images list

sudo ctr --namespace moby snapshots list
sudo ctr --namespace moby snapshots cleanup

`garbage collector should do it by itself`
https://github.com/containerd/containerd/issues/6294




