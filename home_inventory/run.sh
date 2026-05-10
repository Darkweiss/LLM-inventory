#!/usr/bin/with-contenv bashio

CLAUDE_API_KEY=$(bashio::config 'claude_api_key')
APPS_SCRIPT_URL=$(bashio::config 'apps_script_url')

bashio::log.info "API key present: $([ -n "$CLAUDE_API_KEY" ] && echo YES || echo NO)"
bashio::log.info "Apps Script URL present: $([ -n "$APPS_SCRIPT_URL" ] && echo YES || echo NO)"

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
exec python3 /app/server.py 2>&1
