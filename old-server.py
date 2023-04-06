#! /usr/bin/env python3

import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import requests
import json
import sys

DIR = os.path.join( os.getcwd(), "html" )

class RequestHandler(BaseHTTPRequestHandler):
    def do_local_GET(self):
        try:
            # Get the absolute path of the requested file
            abs_path = os.path.abspath(DIR + self.path)

            print( abs_path )
            
            # If the requested path is a directory, try to serve index.html
            if os.path.isdir(abs_path):
                abs_path = os.path.abspath(os.path.join(abs_path, "index.html"))

            # If the file exists, serve it
            if os.path.isfile(abs_path):
                with open(abs_path, 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(file.read())
            # Otherwise, return a 404 error
            else:
                self.send_error(404, 'File not found')
        except Exception as e:
            self.send_error(500, str(e))

    def do_GET_api_doge( self ):
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

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/doge':
            self.do_GET_api_doge()
        else:
            self.do_local_GET()

def run_server():
    listenPort = int(sys.argv[1])
    httpd = HTTPServer(('localhost', listenPort), RequestHandler)
    print( f'Server running on http://localhost:{listenPort}' )
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
