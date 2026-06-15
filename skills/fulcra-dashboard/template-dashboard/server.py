import http.server
import socketserver
import json
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8081))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    # Simulated chat history kept in memory while the server runs
    chat_history = [
        {"role": "assistant", "text": "Telemetry link established. Local relay online. Awaiting parameters. Note: if you have not explicitly asked the agent to connect the envoy, messages sent here will not reach them."}
    ]

    def do_GET(self):
        # Serve the chat history for local-only components
        if self.path == '/api/chat':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"messages": self.chat_history}).encode())
            return
            
        # File Browser backend
        if self.path.startswith('/api/files'):
            import urllib.parse
            import subprocess
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            # Default to root if no path provided
            target_path = params.get('path', [''])[0]
            
            try:
                # Use fulcra-api to list the files
                list_output = subprocess.check_output(["uv", "tool", "run", "fulcra-api", "file", "list", target_path], text=True)
                lines = [line.strip() for line in list_output.strip().split('\n') if line.strip()]
                
                folders = []
                files = []
                
                # We skip the first line if it looks like the upload logging, but `list` output is usually clean
                for line in lines:
                    if line.startswith('⬆️'):
                        continue
                    if line.endswith('/'):
                        folders.append({"name": line[:-1]})
                    else:
                        parts = line.split(maxsplit=4)
                        if len(parts) >= 4:
                            size = parts[0]
                            # Example output: 5B 2026-06-15 11:33PM UTC test.txt
                            date = f"{parts[1]} {parts[2]} {parts[3]}"
                            name = parts[-1]
                            
                            # Fetch stat to get version count
                            full_path = f"{target_path}{name}" if target_path.endswith('/') or not target_path else f"{target_path}/{name}"
                            try:
                                stat_out = subprocess.check_output(["uv", "tool", "run", "fulcra-api", "file", "stat", full_path], text=True, stderr=subprocess.DEVNULL)
                                versions = 0
                                for s_line in stat_out.split('\n'):
                                    if s_line.startswith('Previous Versions:'):
                                        versions = int(s_line.split(':')[1].strip())
                                        break
                                files.append({"name": name, "size": size, "date": date, "versions": versions})
                            except subprocess.CalledProcessError:
                                files.append({"name": name, "size": size, "date": date, "versions": "unknown"})
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"folders": folders, "files": files, "currentPath": target_path}).encode())
                return
            except subprocess.CalledProcessError as e:
                self.send_error(500, f"Error listing files: {str(e)}")
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
                simulated_reply = {"role": "system", "text": "Notice: The Relay is currently dormant. To complete setup, return to your OpenClaw session and explicitly instruct the agent to 'connect the chat envoy', then wait for them to confirm before trying again."}
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
    with socketserver.TCPServer(("127.0.0.1", PORT), DashboardHandler) as httpd:
        print(f"🌲 Primordial Python Server active at http://127.0.0.1:{PORT}")
        print("Serving static files and monitoring /api/chat...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            httpd.server_close()