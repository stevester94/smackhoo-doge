#! /usr/bin/env python3

import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import requests
import json
import sys

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            response = requests.get('https://dog.ceo/api/breeds/image/random')

            if response.status_code == 200:
               j = json.loads( response.content )
               print( j ) 

               response = requests.get( j["message"] )
               if response.status_code == 200:
                  image_bytes = response.content
                  self.wfile.write( image_bytes )
               else:
                  print( "error fetching image content" )
            else:
               print('Error fetching image url')
                
        else:
            self.send_error(404)

def run_server():
    listenPort = int(sys.argv[1])
    httpd = HTTPServer(('localhost', listenPort), RequestHandler)
    print( f'Server running on http://localhost:{listenPort}' )
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
