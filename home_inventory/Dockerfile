FROM ghcr.io/home-assistant/aarch64-base-python:3.11

WORKDIR /app

COPY server.py .
COPY web/ web/
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
