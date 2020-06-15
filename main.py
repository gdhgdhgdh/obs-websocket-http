import asyncio
import json
import simpleobsws
import aiohttp
from aiohttp import web

httpAddress = '0.0.0.0'
httpPort = 4445
httpAuthKey = None
wsAddress = '127.0.0.1'
wsPort = 4444
loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host=wsAddress, port=wsPort, loop=loop)

def statusmessage(message):
    print(str(message) + '...      ', end='', flush=True)

async def handle_emit_request(request):
    """Handler function for all emit-based HTTP requests. Assumes that you know what you are doing because it will never return an error."""
    if ('AuthKey' not in request.headers) and httpAuthKey != None:
        return web.json_response({'status':'error', 'error':'AuthKey header is required.'})
    if httpAuthKey == None or (request.headers['AuthKey'] == httpAuthKey):
        requesttype = request.match_info['type']
        try:
            requestdata = await request.json()
        except json.decoder.JSONDecodeError:
            requestdata = None
        await ws.emit(requesttype, requestdata)
        return web.json_response({'status':'ok'})
    else:
        return web.json_response({'status':'error', 'error':'Bad AuthKey'})

async def handle_call_request(request):
    """Handler function for all call-based HTTP requests."""
    if ('AuthKey' not in request.headers) and httpAuthKey != None:
        return web.json_response({'status':'error', 'error':'AuthKey header is required.'})
    if httpAuthKey == None or (request.headers['AuthKey'] == httpAuthKey):
        requesttype = request.match_info['type']
        try:
            requestdata = await request.json()
        except json.decoder.JSONDecodeError:
            if (await request.text()) == '':
                requestdata = None
        try:
            responsedata = await ws.call(requesttype, requestdata)
        except simpleobsws.MessageTimeout:
            responsedata = {'status':'error', 'error':'The obs-websocket request timed out.'}
        return web.json_response(responsedata)
    else:
        return web.json_response({'status':'error', 'error':'Bad AuthKey'})

app = web.Application()
app.add_routes([web.post('/emit/{type}', handle_emit_request), web.post('/call/{type}', handle_call_request)])
statusmessage('Connecting to obs-websocket')
loop.run_until_complete(ws.connect())
print('[Connected.]')
try:
    web.run_app(app, host=httpAddress, port=httpPort)
except KeyboardInterrupt:
    print('Shutting down...')
