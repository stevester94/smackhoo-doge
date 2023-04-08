#! /usr/bin/env python3
import os
import sys

import asyncio
from aiohttp import web
import mimetypes
import math
import struct
import logging
import numpy as np

HTML_DIR = os.path.join( os.getcwd(), "html" )

async def handle(request):
    path = request.path
    absPath = os.path.abspath( HTML_DIR + path )
    if os.path.isdir(absPath):
        absPath = os.path.abspath(os.path.join(absPath, "index.html"))

    try:
        with open(absPath, 'rb') as f:
            content = f.read()
        content_type, _ = mimetypes.guess_type(absPath)
        if content_type == 'text/html':
            headers = {'Content-Type': 'text/html'}
            headers['Content-Type'] += '; charset=utf-8'
        return web.Response(body=content, headers=headers)
    except FileNotFoundError:
        return web.Response(status=404)

async def audio_generator():
    frequency = 10000  # 10 KHz
    sample_rate = 44100  # CD-quality audio
    amplitude = 1  # Maximum amplitude of 16-bit audio
    duration = 0.5


    while True:
        # frequency -= 500
        if frequency < 20: frequency = 17500
        t = np.linspace(0,duration, int(duration*sample_rate))
        x = amplitude * np.sin(2*np.pi*frequency*t)
        x = x.tolist()
        data = struct.pack('<' + 'f' * len(x), *x)

        yield data
        await asyncio.sleep(duration)

async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for audio_data in audio_generator():
        await ws.send_bytes(audio_data)
    
    return ws

app = web.Application()
app.add_routes([
    web.get('/noise', wshandle),
    web.get('/{tail:.*}', handle),
])

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, port=int(sys.argv[1]) )