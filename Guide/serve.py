#!/usr/bin/env python3
import http.server, socketserver, os
PORT = 5502
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
handler = Handler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Career OS Guide running at http://localhost:{PORT}")
    httpd.serve_forever()
