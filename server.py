#! /usr/bin/env python3

import argparse
import asyncio
import logging
import math
import struct
import json
import fractions
import time
import os
import mimetypes

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from av import AudioFrame
import numpy as np
from utils import UltraSigGen

# Create a class for an audio track
class AudioStreamTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.time = 0
        self.audioGen = UltraSigGen( 10e3, 48000 )
        self.samplerate = 48000
        self.samples = 960 # Num to get each buffer


    async def recv(self):
        logging.info( "recv" )
        # Handle timestamps properly
        if hasattr(self, "_timestamp"):
            self._timestamp += self.samples
            wait = self._start + (self._timestamp / self.samplerate) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0

        # create empty data by default
        # data = np.zeros(self.samples).astype(np.int16)
        data = self.audioGen.get( self.samples )
        data *= 32000
        data = data.astype( np.int16 )

        # Only get speaker data if we have some in the buffer
        # <sig gen here>

        # To convert to a mono audio frame, we need the array to be an array of single-value arrays for each sample (annoying)
        data = data.reshape(data.shape[0], -1).T
        # Create audio frame
        frame = AudioFrame.from_ndarray(data, format='s16', layout='mono')

        # Update time stuff
        frame.pts = self._timestamp
        frame.sample_rate = self.samplerate
        frame.time_base = fractions.Fraction(1, self.samplerate)

        # Return
        return frame


# Create a signaling server using aiohttp
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Create a peer connection
    pc = RTCPeerConnection()

    # Add the audio track to the peer connection
    audioTrack = AudioStreamTrack() 
    pc.addTrack( audioTrack )

    # This basically contains the entire RTC dance
    # async def send_answer():
    #     # Create the session description
    #     recv = json.loads( await ws.receive_str() )
    #     description = RTCSessionDescription(sdp=recv["sdp"], type="offer")

    #     await pc.setRemoteDescription(description)

    #     # Generate the answer
    #     ans = await pc.createAnswer()
    #     await pc.setLocalDescription( ans )

    #     # Send the answer
    #     payload = {
    #         "type": pc.localDescription.type,
    #         "sdp": pc.localDescription.sdp
    #     }
    #     payload = json.dumps( payload )
    #     await ws.send_str( payload )

    # Handle signaling messages
    async for msg in ws:
        if not msg.type == web.WSMsgType.TEXT:
            logging.warn( "Unexpected message type" )
        else:
            j = json.loads(msg.data)

            if j["type"] == "offer":
                description = RTCSessionDescription(sdp=j["sdp"], type="offer")
                await pc.setRemoteDescription(description)
                ans = await pc.createAnswer()
                await pc.setLocalDescription( ans )
                payload = {
                    "type": pc.localDescription.type,
                    "sdp": pc.localDescription.sdp
                }
                payload = json.dumps( payload )
                await ws.send_str( payload )

            if j["type"] == "cmd":
                logging.info( f"Got command: {j}" )
                if j["cmd"] == "increaseFrequency":
                    curFreq_Hz = audioTrack.audioGen.getFrequency_Hz()
                    newFreq_Hz = curFreq_Hz + j["amountHz"]
                                                
                    logging.info( f"Increasing frequency from {curFreq_Hz} to {newFreq_Hz}")
                    audioTrack.audioGen.setFrequency_Hz(newFreq_Hz)
            else:
                logging.warning( f"Not sure what to do with: {j}" )

    return ws

ROOT = "./html"

async def handle(request):
    logging.info( f"handle() called with request: {request}" )
    path = request.path
    absPath = os.path.abspath( ROOT + path )

    # If is directory, get index.html in that dir
    if os.path.isdir(absPath):
        absPath = os.path.abspath(os.path.join(absPath, "index.html"))

    try:
        logging.info( f"Opening {absPath}" )
        with open(absPath, 'rb') as f:
            content = f.read()
        content_type, _ = mimetypes.guess_type(absPath)
        if content_type == 'text/html':
            headers = {'Content-Type': 'text/html'}
            headers['Content-Type'] += '; charset=utf-8'
        elif content_type == "text/javascript":
            headers = {'Content-Type': 'text/javascript'}
            headers['Content-Type'] += '; charset=utf-8'
        elif content_type == "application/javascript":
            headers = {'Content-Type': 'application/javascript'}
            headers['Content-Type'] += '; charset=utf-8'
        else:
            logging.warning( f"Guessed an unknown mimetype: {content_type}, returning status=500")
            return web.Response( status=500 )
        return web.Response(body=content, headers=headers)
    except FileNotFoundError:
        return web.Response(status=404)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC audio stream backend")
    parser.add_argument("--port", type=int, default=8080, help="Port for the signaling server")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Create the signaling server
    app = web.Application()

    app.add_routes([
        web.get('/ws', websocket_handler),
        web.get('/{tail:.*}', handle),
    ])

    # Start the signaling server
    web.run_app(app, port=args.port)
