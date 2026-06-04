import http.server
import socketserver
import json
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8081))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    # Simulated chat history kept in memory while the server runs
    chat_history = [
        {"role": "assistant", "text": "Telemetry link established. Local relay online. Awaiting parameters."}
    ]

    def do_GET(self):
        # Serve the chat history for local-only components
        if self.path == '/api/chat':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"messages": self.chat_history}).encode())
            return
            
        # Download memory files via backend API
        if self.path.startswith('/api/download?file='):
            import urllib.parse
            import subprocess
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            filename = params.get('file', [''])[0]
            
            if not filename:
                self.send_error(400, "Missing file parameter")
                return
                
            # Attempt to download the file using fulcra-api
            try:
                # the filename should be like "agent/treecle/memory/top_of_mind.md"
                # so we download it to a temp path then read and serve it
                tmp_path = f"/tmp/{os.path.basename(filename)}"
                subprocess.run(["uv", "tool", "run", "fulcra-api", "file", "download", filename, tmp_path], check=True, capture_output=True)
                
                with open(tmp_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                # Guess mimetype based on extension
                if filename.endswith('.md'):
                    self.send_header('Content-Type', 'text/markdown; charset=utf-8')
                elif filename.endswith('.gz'):
                    self.send_header('Content-Type', 'application/gzip')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(filename)}"')
                self.end_headers()
                self.wfile.write(content)
                
                # Cleanup temp file
                os.remove(tmp_path)
                return
            except subprocess.CalledProcessError as e:
                self.send_error(500, f"Error downloading file: {e.stderr.decode('utf-8')}")
                return
            except Exception as e:
                self.send_error(500, str(e))
                return
            
        # Serve the static HTML/CSS/JS files
        super().do_GET()

    def do_POST(self):
        # Local-only backend functionality (e.g., OpenClaw chat envoy)
        if self.path == '/api/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                user_msg = data.get('message', '')
                
                # Append user message to history
                if user_msg:
                    self.chat_history.append({"role": "user", "text": user_msg})
                
                # Future: Route this via OpenClaw CLI
                print(f"Received chat request: {data}")
                
                # Generate a simulated response
                simulated_reply = {"role": "system", "text": "Error: Chat Envoy is active but dormant. To wire it up, return to your OpenClaw session and explicitly ask the agent to 'connect the chat envoy'."}
                self.chat_history.append(simulated_reply)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # Return only the new messages to append
                response = {
                    "status": "success", 
                    "messages": [simulated_reply]
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_error(404)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🌲 Primordial Python Server active at http://localhost:{PORT}")
        print("Serving static files and monitoring /api/chat...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            httpd.server_close()