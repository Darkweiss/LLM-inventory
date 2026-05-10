#!/usr/bin/with-contenv bashio
bashio::log.info "Starting Home Inventory server"
exec python3 /app/server.py 2>&1
