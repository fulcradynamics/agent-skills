import http.server
import socketserver
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8081))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    # Serve the static HTML/CSS/JS files
    def do_GET(self):
        # Prevent path traversal outside the public directory
        if '..' in self.path:
            self.send_error(403, "Forbidden")
            return
        super().do_GET()

if __name__ == "__main__":
    # Change to the public directory before serving
    public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')
    if os.path.exists(public_dir):
        os.chdir(public_dir)
    else:
        print("❌ Error: 'public' directory not found. Refusing to serve the root directory to prevent accidental data exposure.")
        sys.exit(1)

    with socketserver.TCPServer(("127.0.0.1", PORT), DashboardHandler) as httpd:
        print(f"🌲 Primordial Python Server active at http://127.0.0.1:{PORT}")
        print("Serving static files...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            httpd.server_close()
