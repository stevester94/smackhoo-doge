#! /usr/bin/env python3

import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import requests


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            image_dir = os.path.join( os.getcwd(), "images" )
            image_file = random.choice(os.listdir(image_dir))
            with open(os.path.join(image_dir, image_file), 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

def run_server():
    httpd = HTTPServer(('localhost', 5984), RequestHandler)
    print('Server running on http://localhost:5984')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
