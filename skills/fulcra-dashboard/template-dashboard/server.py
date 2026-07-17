import http.server
import socketserver
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8081))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    # Serve the static HTML/CSS/JS files
    def do_GET(self):
        super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), DashboardHandler) as httpd:
        print(f"🌲 Primordial Python Server active at http://127.0.0.1:{PORT}")
        print("Serving static files...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            httpd.server_close()
