# !/bin/bash
# Inspired from https://github.com/hhcordero/docker-jmeter-client
# Basically runs jmeter, assuming the PATH is set to point to JMeter bin-dir (see Dockerfile)
#
echo "START Running DataCamp donwloader on `date`"

python /dc-downloader/src/downloader.py $@

echo "END Running DataCamp downloader on `date`"