from http.server import BaseHTTPRequestHandler, HTTPServer
import json, urllib.request

API_KEY = "74f2ae93c52b98aded2cf8cd65d57a43"
BASE = "https://8k.online-cms.ru/api/api.php"
PACK = "85850"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            if self.path != "/activate":
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            mac = body.get("mac", "").upper()
            if ":" not in mac and len(mac) == 12:
                mac = ":".join(mac[i:i+2] for i in range(0,12,2))
            print("Got MAC:", mac)
            url = f"{BASE}?action=new&type=m3u&sub=12&pack={PACK}&country=us&api_key={API_KEY}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as r:
                raw = r.read()
                print("Panel raw:", raw)
                data = json.loads(raw)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            item = data[0] if isinstance(data, list) else data
            if item.get("status") == "true":
                self.wfile.write(json.dumps({
                    "url": item.get("url"),
                    "username": item.get("username"),
                    "password": item.get("password")
                }).encode())
            else:
                self.wfile.write(json.dumps({"error": "panel", "detail": data}).encode())
        except Exception as e:
            print("ERROR:", e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

HTTPServer(("", 3000), Handler).serve_forever()
