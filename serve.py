#!/usr/bin/env python3
"""
Simple HTTP server for the Music Sociology Dashboard.
Serves the dashboard with proper CORS headers for local development.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


def main():
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/dashboard/"
        print()
        print("=" * 50)
        print("  Sound & Society Dashboard")
        print("=" * 50)
        print()
        print(f"  Server running at: http://localhost:{PORT}")
        print(f"  Dashboard URL:     {url}")
        print()
        print("  Press Ctrl+C to stop the server")
        print("=" * 50)
        print()

        # Open browser
        webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
