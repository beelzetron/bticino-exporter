FROM registry.access.redhat.com/ubi8/python-39:latest

LABEL maintainer Lorenzo Dalrio <lorenzo.dalrio@gmail.com>

ENV API_CLIENT_ID ""
ENV API_CLIENT_SECRET ""
ENV API_USERNAME ""
ENV API_PASSWORD ""

USER 0

RUN mkdir /opt/exporter && \
    chown 1001 /opt/exporter && \
    chgrp -R 0 /opt/exporter && \
    chmod -R g=u /opt/exporter

USER 1001

WORKDIR /opt/exporter

COPY requirements.txt /opt/exporter

RUN pip install -r /opt/exporter/requirements.txt

COPY metrics.py /opt/exporter

EXPOSE 9999

CMD python3 /opt/exporter/metrics.py