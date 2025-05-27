import http.server
import socketserver
import os
import signal
import sys

class AutoReloadHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Ensure we serve from the directory containing the HTML file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=current_dir, **kwargs)
        
    def log_message(self, format, *args):
        # Override to provide more detailed logging
        print(f"[Server] {format%args}")

    def end_headers(self):
        # Add auto-reload headers
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def run_server(port=8000):
    try:
        # Allow connections from any network interface
        server_address = ('0.0.0.0', port)
        with socketserver.TCPServer(server_address, AutoReloadHandler) as httpd:
            print(f"Serving mock checkout page at:")
            print(f"* Local:   http://localhost:{port}")
            print(f"* Network: http://0.0.0.0:{port}")
            print("\nPress Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    run_server()
