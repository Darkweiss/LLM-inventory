#!/usr/bin/with-contenv bashio

CLAUDE_API_KEY=$(bashio::config 'claude_api_key')
APPS_SCRIPT_URL=$(bashio::config 'apps_script_url')

if [ -z "$CLAUDE_API_KEY" ]; then
    bashio::log.fatal "claude_api_key is not set in add-on configuration"
    exit 1
fi

if [ -z "$APPS_SCRIPT_URL" ]; then
    bashio::log.fatal "apps_script_url is not set in add-on configuration"
    exit 1
fi

export CLAUDE_API_KEY
export APPS_SCRIPT_URL

bashio::log.info "Starting Home Inventory server on port 8080"
exec python3 /app/server.py
