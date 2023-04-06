#! /usr/bin/env python3
import os
import sys

import asyncio
from aiohttp import web
import mimetypes
import math
import struct


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
    amplitude = 32767  # Maximum amplitude of 16-bit audio
    period = sample_rate / frequency
    values = []
    for i in range(int(period)):
        value = int(amplitude * math.sin((2 * math.pi / period) * i))
        values.append(value)
    data = struct.pack('<' + 'h' * len(values), *values)
    while True:
        yield data
        await asyncio.sleep(1/sample_rate)

async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for audio_data in audio_generator():
        await ws.send(audio_data, binary=True)
    
    return ws

app = web.Application()
app.add_routes([
    web.get('/{tail:.*}', handle),
    web.get('/noise', wshandle),
])

if __name__ == '__main__':
    web.run_app(app, port=int(sys.argv[1]) )