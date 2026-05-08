#!/usr/bin/env python3
"""
Serve the Allure report over HTTP so all assets load correctly.

Usage:
  python serve_report.py          # opens http://localhost:4040
  python serve_report.py 8080     # custom port
"""
import http.server
import socketserver
import webbrowser
import sys
import os

port = int(sys.argv[1]) if len(sys.argv) > 1 else 4040
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
    url = f"http://localhost:{port}"
    print(f"Allure report: {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)
    httpd.serve_forever()
