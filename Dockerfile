FROM python:3.6-alpine

COPY src /dc-downloader/src

RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN cd /dc-downloader/src \
  && apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && apk del build-dependencies

COPY entrypoint.sh /dc-downloader/
COPY downloader.sh /dc-downloader/

ENV WORKDIR '/dc-downloader/src'

WORKDIR ${WORKDIR}

ENTRYPOINT [ "sh", "/dc-downloader/entrypoint.sh" ]
