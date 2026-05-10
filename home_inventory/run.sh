#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Home Inventory server"

if ! command -v python3 > /dev/null 2>&1; then
    bashio::log.fatal "python3 not found!"
    exit 1
fi

bashio::log.info "Python found: $(python3 --version 2>&1)"
bashio::log.info "Options file exists: $([ -f /data/options.json ] && echo YES || echo NO)"

python3 /app/server.py 2>&1
EXIT_CODE=$?
bashio::log.fatal "Server exited with code ${EXIT_CODE}"
