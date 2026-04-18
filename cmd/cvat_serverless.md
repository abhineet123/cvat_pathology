<!-- MarkdownTOC -->

- [functions       @ deploy](#functions___deploy_)
  - [microsam       @ functions](#microsam___function_s_)
    - [hp       @ microsam/functions](#hp___microsam_functions_)
    - [lm       @ microsam/functions](#lm___microsam_functions_)
    - [mi       @ microsam/functions](#mi___microsam_functions_)
    - [dbg       @ microsam/functions](#dbg___microsam_functions_)
  - [cellpose       @ functions](#cellpose___function_s_)
  - [cellvit       @ functions](#cellvit___function_s_)
    - [sam       @ cellvit/functions](#sam___cellvit_function_s_)
    - [hipt       @ cellvit/functions](#hipt___cellvit_function_s_)
    - [virchow       @ cellvit/functions](#virchow___cellvit_function_s_)
  - [instanseg       @ functions](#instanseg___function_s_)
    - [debug       @ instanseg/functions](#debug___instanseg_function_s_)
  - [stardist       @ functions](#stardist___function_s_)
  - [openvino       @ functions](#openvino___function_s_)
  - [iog       @ functions](#iog___function_s_)
  - [sam       @ functions](#sam___function_s_)
  - [retinanet_r101       @ functions](#retinanet_r101___function_s_)
- [debug](#debug_)
    - [vscode       @ debug/](#vscode___debug_)
    - [manage       @ debug/](#manage___debug_)

<!-- /MarkdownTOC -->
<a id="functions___deploy_"></a>
# functions       @ deploy-->cvat_setup
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

<a id="microsam___function_s_"></a>
## microsam       @ functions-->cvat_serverless
docker system prune -a

./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam
docker logs nuclio-nuclio-pth-microsam -f
nuctl delete function pth-microsam --platform local --force

docker exec -it nuclio-nuclio-pth-microsam /bin/bash
ssh-keygen -q -t rsa -N '' -C "microsam" -f /root/.ssh/id_rsa
cat /root/.ssh/id_rsa.pub
apt update && apt install ssh nano
nano /root/.ssh/config
ssh -R 5679:localhost:5679 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null x99

<a id="hp___microsam_functions_"></a>
### hp       @ microsam/functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_hp_huge
docker logs nuclio-nuclio-pth-microsam_hp_huge -f
nuctl delete function pth-microsam_hp_huge --platform local --force

./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_hp_base
docker logs nuclio-nuclio-pth-microsam_hp_base -f
nuctl delete function pth-microsam_hp_base --platform local --force

./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_hp_large
docker logs nuclio-nuclio-pth-microsam_hp_large -f
nuctl delete function pth-microsam_hp_large --platform local --force

<a id="lm___microsam_functions_"></a>
### lm       @ microsam/functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_lm_base
docker logs nuclio-nuclio-pth-microsam_lm_base -f
nuctl delete function pth-microsam_lm_base --platform local --force

./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_lm_large
docker logs nuclio-nuclio-pth-microsam_lm_large -f
nuctl delete function pth-microsam_lm_large --platform local --force

<a id="mi___microsam_functions_"></a>
### mi       @ microsam/functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_mi_base
docker logs nuclio-nuclio-pth-microsam_mi_base -f
nuctl delete function pth-microsam_mi_base --platform local --force

<a id="dbg___microsam_functions_"></a>
### dbg       @ microsam/functions-->cvat_serverless
sudo chown -R abhineet: /data/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/5343
sudo chown -R root:root /data/containerd

sudo ls -l /data/containerd
sudo ls -l /data/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots

watch sudo cat /data/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/5343/fs/opt/nuclio/microsam/nuctl_outputs.log
sudo ls /data/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/5283/fs/opt/nuclio/microsam/nuctl_outputs.log

./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam_dummy
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam311
./serverless/deploy_gpu.sh serverless/pytorch/microsam microsam310

nuctl delete function pth-microsam310 --platform local --force
nuctl delete function pth-microsam311 --platform local --force

<a id="cellpose___function_s_"></a>
## cellpose       @ functions-->cvat_serverless
nuctl get function --platform local

./serverless/deploy_gpu.sh serverless/pytorch/cellpose cellpose
docker logs nuclio-nuclio-pth-cellpose -f

docker exec -it nuclio-nuclio-pth-cellpose /bin/bash

nuctl delete function pth-cellpose --platform local --force
docker system prune -a

<a id="cellvit___function_s_"></a>
## cellvit       @ functions-->cvat_serverless
<a id="sam___cellvit_function_s_"></a>
### sam       @ cellvit/functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/cellvit cellvit
docker logs nuclio-nuclio-pth-cellvit-sam -f

<a id="hipt___cellvit_function_s_"></a>
### hipt       @ cellvit/functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/cellvit cellvit-hipt
docker logs nuclio-nuclio-pth-cellvit-hipt -f

<a id="virchow___cellvit_function_s_"></a>
### virchow       @ cellvit/functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/cellvit cellvit-virchow
docker logs nuclio-nuclio-pth-cellvit-virchow -f

<a id="instanseg___function_s_"></a>
## instanseg       @ functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/instanseg instanseg
docker logs nuclio-nuclio-pth-instanSeg -f
nuctl delete function pth-instanSeg --platform local --force

<a id="debug___instanseg_function_s_"></a>
### debug       @ instanseg/functions-->cvat_serverless
docker exec -it nuclio-nuclio-pth-instanSeg /bin/bash
cat /root/.ssh/id_rsa.pub
ssh -R 5678:localhost:5678 x99

<a id="stardist___function_s_"></a>
## stardist       @ functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/stardist stardist
docker logs nuclio-nuclio-pth-stardist -f
nuctl delete function pth-stardist --platform local --force

<a id="openvino___function_s_"></a>
## openvino       @ functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/openvino/dextr
./serverless/deploy_gpu.sh serverless/openvino/omz/public/yolo-v3-tf

./serverless/deploy_cpu.sh serverless/openvino/dextrpublic
./serverless/deploy_cpu.sh serverless/openvino/omz//yolo-v3-tf
./serverless/deploy_cpu.sh serverless/openvino/omz/public/mask_rcnn_inception_resnet_v2_atrous_coco

<a id="iog___function_s_"></a>
## iog       @ functions-->cvat_serverless
./serverless/deploy_cpu.sh serverless/pytorch/shiyinzhang/iog
<a id="sam___function_s_"></a>
## sam       @ functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/facebookresearch/sam
<a id="retinanet_r101___function_s_"></a>
## retinanet_r101       @ functions-->cvat_serverless
./serverless/deploy_gpu.sh serverless/pytorch/facebookresearch/detectron2/retinanet_r101

<a id="debug_"></a>
# debug 
docker logs cvat_db -f
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

<a id="vscode___debug_"></a>
### vscode       @ debug/-->cvat_serverless
https://docs.cvat.ai/docs/guides/serverless-tutorial/#debugging-a-serverless-function
docker exec -it nuclio-nuclio-pth-microsam /bin/bash
cat /root/.ssh/id_rsa.pub

<a id="manage___debug_"></a>
### manage       @ debug/-->cvat_serverless
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





