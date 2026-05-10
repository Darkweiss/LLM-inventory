# Home Inventory — Project Context

## What this is

A voice-searchable home inventory system for Luka. Physical storage boxes are tagged with NFC stickers. Tapping a tag opens a web app (hosted on Home Assistant Green) where you can speak or type questions about the inventory, answered by Claude AI.

## Current status

Fully working end-to-end:
- Google Apps Script endpoint returns inventory JSON ✅
- Python backend server proxies Claude API calls ✅
- Single-page web app with voice + text input ✅
- Hosted as a Home Assistant add-on on HA Green ✅
- Accessible directly at `http://HA_IP:8080` without HA login (for NFC tags) ✅
- NFC tags write a URL with `?box=ID` to pre-load a specific box ✅

## Repository

GitHub: `https://github.com/Darkweiss/LLM-inventory`
Local: `/Users/lux/Documents/GitHub/LLM inventory/`

## Key files

| File | Purpose |
|------|---------|
| `home_inventory/server.py` | Python HTTP server — serves HTML, proxies Claude API, fetches inventory |
| `home_inventory/web/index.html` | Single-page web app — voice/text input, displays answers |
| `home_inventory/run.sh` | HA add-on startup script |
| `home_inventory/config.yaml` | HA add-on manifest (current version inside) |
| `home_inventory/Dockerfile` | `FROM ghcr.io/home-assistant/aarch64-base:3.20` + apk python3 |
| `google-apps-script/Code.gs` | Apps Script that exposes Google Sheet as JSON |
| `.env` | Local dev secrets — `CLAUDE_API_KEY` and `APPS_SCRIPT_URL` (gitignored) |

## Architecture

- **Data**: Google Sheets with two tabs — `Inventory` (items) and `Box names` (boxes)
- **Sheet access**: Google Apps Script web endpoint (deployed as public, URL-secret)
- **Backend**: Pure Python stdlib server — reads `/data/options.json` for HA config, falls back to `.env` for local dev
- **Frontend**: Fetches inventory via `/api/inventory`, sends questions to `/api/ask` using relative URLs (required for HA ingress compatibility)
- **Model**: `claude-haiku-4-5-20251001`
- **Hosting**: HA add-on with ingress (port 8080) + direct port exposure (also 8080)

## Key decisions made

- **No pip dependencies** — server.py uses Python stdlib only
- **Relative URLs** (`api/inventory` not `/api/inventory`) — required because HA ingress serves the app under a subpath
- **Python reads `/data/options.json` directly** — more reliable than passing env vars through bashio
- **Claude API called server-side** — browser-to-Claude calls are blocked by CORS; the Python server proxies them
- **Direct port 8080 exposed** — bypasses HA authentication for NFC tag use case

## Deployment workflow

1. Make changes locally
2. Bump version in `home_inventory/config.yaml`
3. `git add`, `git commit`, `git push`
4. In HA: Add-on Store → three-dot menu → Check for updates → Update

## Google Sheets structure

**Inventory tab**: Box ID | Box Name | Box Location | Item Name | Category | Tags | Quantity | Notes
**Box names tab**: Box ID | Box Name | Location | Color/Label | NFC Tag ID

Box IDs are integers (1, 2, 3...).

## Future phases (not built yet)

- Add/remove items via voice commands
- Photo-to-inventory via Claude vision API
- HA dashboard card showing box contents
- Low stock alerts / automations
- Multi-language support
