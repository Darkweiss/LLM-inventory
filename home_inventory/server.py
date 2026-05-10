import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

# Load config from HA add-on options, .env file, or environment variables
_ha_options = '/data/options.json'
if os.path.exists(_ha_options):
    with open(_ha_options) as f:
        _opts = json.load(f)
    CLAUDE_API_KEY  = _opts.get('claude_api_key', '')
    APPS_SCRIPT_URL = _opts.get('apps_script_url', '')
else:
    _env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(_env_path):
        with open(_env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
    CLAUDE_API_KEY  = os.environ.get('CLAUDE_API_KEY', '')
    APPS_SCRIPT_URL = os.environ.get('APPS_SCRIPT_URL', '')

PORT = int(os.environ.get('PORT', 8080))

SYSTEM_PROMPT = """\
You are a home inventory assistant. Answer concisely in 1-3 sentences — your answer will be read aloud.
Always mention the Box ID and Box Name when directing the user to a location.
If an item is not in the inventory, say "I don't see that in the inventory."
Do not hallucinate items. Only reference data in the provided inventory.
Do not use markdown formatting — no asterisks, no bold, no bullet points. Plain text only.

DATA SCHEMA:
- inventory: array of items with fields: Box ID, Box Name, Box Location, Item Name, Category, Tags, Quantity, Notes
- boxes: array of boxes with fields: Box ID, Box Name, Location, Color/Label, NFC Tag ID\
"""


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self._serve_file(os.path.join(os.path.dirname(__file__), 'web', 'index.html'), 'text/html')
        elif self.path == '/api/inventory':
            try:
                inventory = self._fetch_inventory()
                self._json(200, inventory)
            except Exception as e:
                self._json(500, {'error': str(e)})
        else:
            self._respond(404, 'text/plain', b'Not found')

    def do_POST(self):
        if self.path == '/api/ask':
            length = int(self.headers.get('Content-Length', 0))
            body   = json.loads(self.rfile.read(length))
            question = body.get('question', '').strip()
            box_id   = body.get('box')

            if not question:
                self._json(400, {'error': 'No question provided'})
                return

            try:
                inventory_data = self._fetch_inventory()
                answer = self._ask_claude(question, box_id, inventory_data)
                self._json(200, {'answer': answer})
            except Exception as e:
                self._json(500, {'error': str(e)})
        else:
            self._respond(404, 'text/plain', b'Not found')

    def _fetch_inventory(self):
        with urllib.request.urlopen(APPS_SCRIPT_URL, timeout=10) as r:
            return json.loads(r.read())

    def _ask_claude(self, question, box_id, inventory_data):
        system = SYSTEM_PROMPT
        if box_id:
            system += f'\n\nThe user is currently viewing box {box_id}. Prioritise that box in your answer, but use the full inventory if the question is about something else.'

        messages = [
            {'role': 'user',      'content': 'Here is the current inventory:\n' + json.dumps(inventory_data)},
            {'role': 'assistant', 'content': 'Inventory loaded. What would you like to know?'},
            {'role': 'user',      'content': question},
        ]

        payload = json.dumps({
            'model':      'claude-haiku-4-5-20251001',
            'max_tokens': 512,
            'system':     system,
            'messages':   messages,
        }).encode()

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'x-api-key':         CLAUDE_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type':      'application/json',
            },
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())

        return data['content'][0]['text']

    def _serve_file(self, path, content_type):
        try:
            with open(path, 'rb') as f:
                content = f.read()
            self._respond(200, content_type, content)
        except FileNotFoundError:
            self._respond(404, 'text/plain', b'File not found')

    def _json(self, status, obj):
        self._respond(status, 'application/json', json.dumps(obj).encode())

    def _respond(self, status, content_type, body):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f'[{self.address_string()}] {fmt % args}')


if __name__ == '__main__':
    print('server.py startup', flush=True)
    print(f'CLAUDE_API_KEY set: {bool(CLAUDE_API_KEY)}', flush=True)
    print(f'APPS_SCRIPT_URL set: {bool(APPS_SCRIPT_URL)}', flush=True)
    if not CLAUDE_API_KEY:
        print('ERROR: claude_api_key is empty', flush=True)
        raise SystemExit(1)
    if not APPS_SCRIPT_URL:
        print('ERROR: apps_script_url is empty', flush=True)
        raise SystemExit(1)
    print(f'Serving on http://0.0.0.0:{PORT}', flush=True)
    HTTPServer(('', PORT), Handler).serve_forever()
