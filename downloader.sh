# !/bin/bash
#
# Run DCDownloader Docker image with options

NAME="dc_downloader"
IMAGE="dc_downloader"

# Finally run
sudo docker stop ${NAME} > /dev/null 2>&1
sudo docker rm ${NAME} > /dev/null 2>&1
sudo docker run --name ${NAME} -i -v ${PWD}:${PWD} -w ${PWD} ${IMAGE} $@