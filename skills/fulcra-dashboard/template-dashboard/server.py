import http.server
import socketserver
import json
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8081))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    # If chat.json exists, we'll load it, otherwise use a default dict structure
    def get_chat_history(self):
        if os.path.exists('chat.json'):
            try:
                with open('chat.json', 'r') as f:
                    data = json.load(f)
                    # Migrate old list format to dict format if necessary
                    if isinstance(data, list):
                        return {"agent_connected": False, "messages": data}
                    return data
            except:
                pass
        return {
            "agent_connected": False,
            "messages": [
                {"role": "assistant", "text": "Telemetry link established. Local relay online. Awaiting parameters. Note: if you have not explicitly asked the agent to connect the envoy, messages sent here will not reach them."}
            ]
        }

    def save_chat_history(self, history):
        with open('chat.json', 'w') as f:
            json.dump(history, f, indent=2)

    def do_GET(self):
        # Serve the chat history for local-only components
        if self.path == '/api/chat':
            history = self.get_chat_history()
            
            # Determine if the agent is processing a message.
            # It's processing if the agent has connected, the last message is from the user, and it has been marked as read.
            messages = history.get("messages", [])
            agent_processing = False
            if messages:
                last_msg = messages[-1]
                if last_msg.get("role") == "user" and last_msg.get("read") is True:
                    agent_processing = True

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "messages": messages,
                "agent_processing": agent_processing
            }).encode())
            return
            
        # Agent endpoint to retrieve unread messages and mark as read
        if self.path == '/api/chat/unread':
            history = self.get_chat_history()
            
            # Mark that the agent successfully connected to fetch messages
            history["agent_connected"] = True
            
            messages = history.get("messages", [])
            unread = [msg for msg in messages if msg.get("role") == "user" and not msg.get("read")]
            
            # Mark them as read
            for msg in messages:
                if msg.get("role") == "user":
                    msg["read"] = True
            
            # Always save to update the agent_connected status even if no unread messages
            self.save_chat_history(history)
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"unread_messages": unread}).encode())
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
                
                history = self.get_chat_history()
                messages = history.get("messages", [])
                
                new_messages_to_return = []
                
                if user_msg:
                    # Append user message to history and mark unread
                    messages.append({"role": "user", "text": user_msg, "read": False})
                    history["messages"] = messages
                    
                    # If the agent has never connected to poll, append an error immediately
                    if not history.get("agent_connected"):
                        error_msg = {"role": "system", "text": "Notice: The agent has not been connected to this dashboard. Please return to your OpenClaw session and ask the agent to 'connect the chat envoy using the fulcra-dashboard skill'."}
                        messages.append(error_msg)
                        new_messages_to_return.append(error_msg)
                    
                    self.save_chat_history(history)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # The frontend will append any immediate system replies
                response = {
                    "status": "success", 
                    "messages": new_messages_to_return
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