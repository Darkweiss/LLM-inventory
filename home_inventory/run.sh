#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Home Inventory server"
bashio::log.info "Python: $(python3 --version 2>&1)"
bashio::log.info "Options file: $([ -f /data/options.json ] && echo YES || echo NO)"

PYTHONUNBUFFERED=1 python3 /app/server.py 2>&1
bashio::log.fatal "Server exited with code $?"
