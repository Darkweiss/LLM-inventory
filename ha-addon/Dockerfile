ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base-python:3.12
FROM $BUILD_FROM

WORKDIR /app

COPY server.py .
COPY web/ web/

RUN pip3 install --no-cache-dir --break-system-packages urllib3

COPY ha-addon/run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
