# Home Inventory Voice Search

A voice-searchable home inventory system. Physical storage boxes are tagged with NFC stickers. Tapping a tag opens a web app where you can speak or type questions about your inventory, answered by Claude AI.

## How it works

```
NFC tap → browser opens web app → speak or type question
→ Python server fetches inventory from Google Sheets
→ Claude answers in plain English
→ Answer displayed and read aloud
```

## Stack

| Component | Choice |
|-----------|--------|
| Data store | Google Sheets |
| Sheet API | Google Apps Script web endpoint |
| LLM | Claude Haiku (claude-haiku-4-5-20251001) |
| Backend | Python (stdlib only, no dependencies) |
| Frontend | Single HTML file, Web Speech API |
| Hosting | Home Assistant add-on (Docker) |
| NFC | NFC Tools app → writes URL to tag |

## Repository structure

```
├── google-apps-script/
│   └── Code.gs              # Apps Script endpoint — returns inventory as JSON
├── home_inventory/          # HA add-on
│   ├── config.yaml          # Add-on manifest
│   ├── Dockerfile           # Alpine + Python 3.12
│   ├── run.sh               # Startup script
│   ├── server.py            # Python HTTP server (serves HTML + proxies Claude)
│   └── web/
│       └── index.html       # Single-page web app
├── repository.yaml          # Identifies repo as HA add-on repository
└── .env                     # Local dev secrets (gitignored)
```

## Google Sheets structure

**Inventory sheet** — one row per item:

| Box ID | Box Name | Box Location | Item Name | Category | Tags | Quantity | Notes |
|--------|----------|--------------|-----------|----------|------|----------|-------|

**Box names sheet** — one row per box:

| Box ID | Box Name | Location | Color/Label | NFC Tag ID |
|--------|----------|----------|-------------|------------|

## Setup

### 1. Google Apps Script endpoint

1. Open your Google Sheet → **Extensions → Apps Script**
2. Paste the contents of `google-apps-script/Code.gs`
3. Replace `YOUR_SPREADSHEET_ID_HERE` with your sheet ID (from the sheet URL)
4. **Deploy → New deployment** → Type: Web app → Execute as: Me → Access: **Anyone**
5. Copy the `/exec` URL

### 2. Install the HA add-on

1. In Home Assistant: **Settings → Add-ons → Add-on Store → three-dot menu → Repositories**
2. Add `https://github.com/Darkweiss/LLM-inventory`
3. Find **Home Inventory** in the store and install it
4. Go to the **Configuration** tab and enter:
   - `claude_api_key`: your Anthropic API key
   - `apps_script_url`: the Apps Script `/exec` URL from step 1
5. Start the add-on

### 3. Access the app

The app runs on two URLs:
- **With HA login** (via ingress): `http://homeassistant.local:8123` → sidebar
- **Direct access, no login** (for NFC tags): `http://YOUR_HA_IP:8080`

### 4. NFC tags

Using NFC Tools (iOS or Android):
1. **Write → Add a record → URL**
2. Enter `http://YOUR_HA_IP:8080/?box=1` (replace `1` with the Box ID)
3. Write to tag and stick on the box

Tapping the tag opens the app pre-filtered to that box's contents.

## Local development

Create a `.env` file in the project root:

```
CLAUDE_API_KEY=sk-ant-...
APPS_SCRIPT_URL=https://script.google.com/macros/s/.../exec
```

Then run:

```bash
python3 home_inventory/server.py
```

Open `http://localhost:8080` in Chrome.

## Cost

~$0.0003 per query using Claude Haiku. At 10 queries/day that's roughly $0.10/month.
