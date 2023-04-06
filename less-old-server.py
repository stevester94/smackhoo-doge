#! /usr/bin/env python3

import http.server
import socketserver
import logging
import websocket
import select
import os 

PORT = 5984

# Disable HTTP server logging messages
logging.getLogger().setLevel(logging.ERROR)

HTML_DIR = os.path.join( os.getcwd(), "html" )

print( "smegmag", HTML_DIR )

class WebSocketHandler(websocket.WebSocket):
    def __init__(self, sock):
        super().__init__(sock)
        self.request = None
    
    def fileno(self):
        return self.sock.fileno()
    
    def set_request(self, request):
        self.request = request
    
    def send(self, data):
        # WebSocket send method
        return super().send(data, opcode=websocket.ABNF.OPCODE_BINARY)

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if hasattr( self, "headers" ):
            if self.headers.get('Upgrade', '').lower() == 'websocket':
                self.handle_websocket()

        absPath = os.path.abspath( HTML_DIR + self.path )

        if os.path.isdir(absPath):
            absPath = os.path.abspath(os.path.join(absPath, "index.html"))
        self.path = absPath

        # If the file exists, serve it
        if os.path.isfile(absPath):
            with open(absPath, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        # Otherwise, return a 404 error
        else:
            self.send_error(404, 'File not found')

    def handle_websocket(self):
        print( "Handling a websocket" )
        ws = self.websocket = WebSocketHandler(sock=self.request)
        ws.set_request(self)
        # Notify server that a new WebSocket connection has been established
        self.server.websocket_handlers.append(ws)
        
        while True:
            # Check if the WebSocket is closed
            if ws.closed:
                break
            
            # Use select to check if there is any data available to read
            r, _, _ = select.select([ws], [], [], 1)
            if r:
                data = ws.recv()
                # Notify server that new data has been received
                self.server.handle_websocket_data(self, data)

        # Notify server that the WebSocket connection has been closed
        self.server.websocket_handlers.remove(ws)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        self.websocket_handlers = []
        super().__init__(server_address, RequestHandlerClass)

    def handle_websocket_data(self, request_handler, data):
        # Broadcast the received data to all connected WebSocket clients
        for handler in self.websocket_handlers:
            if handler is not request_handler:
                handler.send(data)

# Create server and start serving
httpd = Server(('localhost', PORT), RequestHandler)
print(f"Server started at http://localhost:{PORT}")
httpd.serve_forever()