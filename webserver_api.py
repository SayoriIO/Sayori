#!/usr/bin/env python3
# API Overview
# ------------

# There are three accepted parameters, `poem`, `font` and `bg`.
# `poem` is the only required parameter, and specifies the content of the poem to generate.
# `font` is optional, and if it is not a supported font, it will default to DEFAULT_FONT (usually `m1`).
# `bg` is optional, and if it is not a supported background, it will default to the default background.
# Parameters can either be sent by a JSON body, or by a query string (?poem=Hello%20world&font=y1&bg=y2)

# Requests can either be a GET or a POST, with the former being allowed to support browsers.
# Both methods of submitting data are supported with both methods,
# however most things that send a GET will only allow the query string method (as far as I am aware).
import image
import os
import hashlib
import redis
import asyncio
import gzip
import logging
import json
import aiohttp_cors

from io import StringIO, BytesIO
from PIL import Image
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor

# Redis cache, defaults to localhost
CACHE = redis.StrictRedis(host=os.environ.get('REDIS_URL') or 'localhost')
loop = asyncio.new_event_loop()
# Scale workers to the amount of CPU present in the host
executor = ThreadPoolExecutor(max_workers=os.cpu_count())

async def handle_post(req):
    body = await req.text()
    is_json = True

    if not body:
        body = req.query
        is_json = False

    if not body:
        return web.json_response({'error': 'No body or query string.', 'code': 0}, status=400)

    if is_json:
        # JSON might not be valid, let's check first
        try:
            body = json.loads(body)
        except ValueError as e:
            return web.json_response({'error': 'Invalid request.', 'code': 5}, status=400)

    if 'poem' not in body:
        return web.json_response({'error': 'Missing required field: "poem".', 'code': 1}, status=400)

    if not isinstance(body['poem'], str):
        return web.json_response({'error': 'Field "poem" is not a string.', 'code': 2}, status=400)

    if not body['poem']:
        return web.json_response({'error': 'Field "poem" is empty.', 'code': 3}, status=400)

    if 'font' in body and body['font'] not in image.FONTS:
        return web.json_response({'error': 'Unsupported font.', 'valid_fonts': image.FONTS.keys(), 'code': 4}, status=400)
    
    if body.get('bg') not in image.BACKGROUNDS:
        # ignore setting and just fallback immediately to default
        body['bg'] = None

    poem = body['poem']
    font = body.get('font', image.DEFAULT_FONT)
    bg = body['bg'] or image.BACKGROUNDS['default']
    output = StringIO()
    hash = hashlib.md5((body['poem'] + font + bg).encode('utf-8')).hexdigest()

    # Check if the image is cached
    if CACHE.exists(hash):
        # We already generated this before, so 302 to the cached image
        return web.json_response({'url': f'/p/{hash}'}, status=200)
    else:
        im = image.generate_image(poem, font, bg)
        # Give it an expiry of 6 hours to save space
        CACHE.set(str(hash), gzip.compress(im.getvalue()), ex=21600)

        # Dispose the buffer to save some bytes.
        im.flush()
        im.close()
        
        return web.json_response({'url': f'/p/{hash}'}, status=200)


async def handle_get(req):
    
    hash = req.match_info['hash']

    if not CACHE.exists(hash):
        return web.Response(body="Not found.", status=404)
    else:
        data = gzip.decompress(CACHE.get(hash)) # type: ignore
        im = BytesIO(data)

        return web.json_response(body=im.getvalue(), status=200, content_type='image/png')

# Finally setup routes and start the server
app = web.Application()
logger = logging.getLogger('aiohttp.access')

app.router.add_route('GET', '/p/{hash}', handle_get)
app.router.add_route('POST', '/generate', handle_post)

# Setup CORS
aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_methods=["GET", "POST", "OPTIONS"],
        expose_headers="*",
        allow_headers="*",
    )
})

logging.basicConfig(format= '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

if __name__ == '__main__':
    logger.info(f"Starting server on port {os.environ.get('PORT') or 7270}")
    logger.info(f"Using {os.cpu_count()} workers")
    logger.info(f"Using Redis at {os.environ.get('REDIS_URL') or 'redis://localhost:6379'}")
    web.run_app(app, port=int(os.environ.get('PORT') or 7270))