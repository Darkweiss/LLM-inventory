FROM ghcr.io/home-assistant/aarch64-base:3.20

RUN apk add --no-cache python3

WORKDIR /app

COPY server.py .
COPY web/ web/
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
