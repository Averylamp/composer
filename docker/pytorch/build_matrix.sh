#!/bin/bash
set -exuo pipefail

LINUX_DISTRO="ubuntu20.04"
# Google colab requires python 3.7
PYTHON_VERSIONS="3.7 3.8 3.9"
PYTORCH_VERSIONS="1.9.1 1.10.0"
TORCHVISION_VERSION_1_10_0="0.11.1"
TORCHVISION_VERSION_1_9_1="0.10.1"
CUDA_VERSIONS_1_9_1="cu111 cpu"
CUDA_VERSIONS_1_10_0="cu111 cu113 cpu"
BASE_IMAGE_cu111="nvidia/cuda:11.1.1-cudnn8-runtime-${LINUX_DISTRO}"
BASE_IMAGE_cu113="nvidia/cuda:11.3.1-cudnn8-runtime-${LINUX_DISTRO}"
BASE_IMAGE_cpu="ubuntu:20.04"

for PYTHON_VERSION in ${PYTHON_VERSIONS[@]}; do
    for PYTORCH_VERSION in ${PYTORCH_VERSIONS[@]}; do
        PYTORCH_VERSION_STRING=$(echo $PYTORCH_VERSION | tr '.' '_')
        CUDA_VERSION_VARNAME="CUDA_VERSIONS_${PYTORCH_VERSION_STRING}"
        CUDA_VERSIONS="${!CUDA_VERSION_VARNAME}"
        TORCHVISION_VERSION_VARNAME="TORCHVISION_VERSION_$PYTORCH_VERSION_STRING"
        TORCHVISION_VERSION="${!TORCHVISION_VERSION_VARNAME}"
        for CUDA_VERSION in ${CUDA_VERSIONS[@]}; do
            BASE_IMAGE_VARNAME="BASE_IMAGE_${CUDA_VERSION}"
            BASE_IMAGE="${!BASE_IMAGE_VARNAME}"
            ARGS="TAG=mosaicml/pytorch:${PYTORCH_VERSION}_${CUDA_VERSION}-python${PYTHON_VERSION}-${LINUX_DISTRO}"
            ARGS="$ARGS BASE_IMAGE='$BASE_IMAGE'"
            ARGS="$ARGS CUDA_VERSION='${CUDA_VERSION}'"
            ARGS="$ARGS LINUX_DISTRO='${LINUX_DISTRO}'"
            ARGS="$ARGS PYTHON_VERSION='$PYTHON_VERSION'"
            ARGS="$ARGS PYTORCH_VERSION='$PYTORCH_VERSION'"
            ARGS="$ARGS TORCHVISION_VERSION='$TORCHVISION_VERSION'"
            echo $ARGS
        done
    done
done
