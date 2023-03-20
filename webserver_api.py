import image
import os
import hashlib
import redis
import asyncio
import gzip
import logging

from io import StringIO
from PIL import Image
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor

# Redis cache, defaults to localhost
CACHE = redis.Redis(host=os.environ.get('REDIS_URL') or 'redis://localhost:6379', db=0)
loop = asyncio.new_event_loop()
# Scale workers to the amount of CPU present in the host
executor = ThreadPoolExecutor(max_workers=os.cpu_count())

@web.middleware
async def cors_middleware(req, handler):
    resp = await handler(req)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return resp

# Return 200 to allow option requests to pass through
# The CORS middleware above sets the appropriate headers
async def handle_options(req):
    return web.Response(status=200)

async def handle_post(req):
    body = await req.text()
    is_json = True

    if not body:
       body = req.query
       is_json = False
    
    if not body:
        return web.json_response({'error': 'No body or query parameters provided'}, status=400)

    if 'poem' not in body:
        return web.json_response({'error': 'No poem provided'}, status=400)
    
    if not isinstance(body['poem'], str):
        return web.json_response({'error': 'Poem must be a string'}, status=400)
    
    if not body['poem']:
        return web.json_response({'error': 'Poem cannot be empty'}, status=400)
    
    if 'font' in  body and body['font'] not in image.FONTS:
        return web.json_response({'error': 'Invalid font'}, status=400)
    
    if body.get('bg') not in image.BACKGROUNDS:
        # ignore setting and just fallback immediately to default
        body['bg'] = None

    poem = body['poem']
    font = body.get('font', image.DEFAULT_FONT)
    bg = body['bg'] or image.BACKGROUNDS['default']
    hash = hashlib.md5((body['poem'] + font + bg).encode('utf-8')).hexdigest()

    # Check if the image is cached
    if CACHE.exists(hash):
        # Redirect to GET route
        web.Response(status=302, headers={'Location': '/p/' + hash})
    else:
        # Generate the image
        im = await loop.run_in_executor(executor, image.generate, poem, font, bg)

        # Give it an expiry of 6 hours to save space
        CACHE.set(str(hash), gzip.compress(im.getvalue()), ex=21600)

        # Redirect to GET route
        return web.Response(status=302, headers={'Location': '/p/' + hash})


async def handle_get(req):
    
    hash = req.match_info['hash']

    if not CACHE.exists(hash):
        return web.Response(message="", status=404)
    else:
        output = StringIO()
        im = Image.open(gzip.decompress((CACHE.get(hash))))
        im.save(output, format=im.format)

        return web.Response(body=output.getvalue(), content_type='image/png')

# Finally setup routes and start the server
app = web.Application(middlewares=[cors_middleware])

app.router.add_route('GET', '/p/{hash}', handle_get)
app.router.add_route('POST', '/p', handle_post)
app.router.add_route('OPTIONS', '/p', handle_options)

if __name__ == '__main__':
    logging.info(f"Starting server on port {os.environ.get('PORT') or 7270}")
    logging.info(f"Using {os.cpu_count()} workers")
    logging.info(f"Using Redis at {os.environ.get('REDIS_URL') or 'redis://localhost:6379'}")
    web.run_app(app, port=int(os.environ.get('PORT') or 7270))