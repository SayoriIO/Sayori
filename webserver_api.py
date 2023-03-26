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
import os
import hashlib
import image
import redis
import gzip
import logging
import json

from io import BytesIO
from flask import Flask, Request, Response, request

# Redis cache, defaults to localhost
CACHE = redis.StrictRedis(host=os.environ.get('REDIS_URL') or 'localhost')
app = Flask(__name__)

# FIXME: We get UnicodeDecodeError for every request, we will force ASCII to prevent some errors
app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['GET'])
async def handle_request(req: Request = request):
    body = req.args.to_dict()

    if 'poem' not in body:
        return Response('Missing required field: poem', status=400)

    if not isinstance(body['poem'], str):
        return Response("Field 'poem' is not a string.", status=400)

    if not body['poem']:
        return Response("Field 'poem' is empty.", status=400)

    if 'font' in body and body['font'] not in image.FONTS:
        return Response(f'Invalid font, valid fonts are {list(image.FONTS.keys())}', status=400)

    poem = body['poem']
    font = body.get('font', image.DEFAULT_FONT)
    bg = body.get('bg', image.BACKGROUNDS['default'])
    # trim hash if its more than 64 characters
    hash = hashlib.md5((body['poem']).encode('utf-8')).hexdigest()[:64]

    # Check if the image is cached
    if CACHE.exists(hash):
        # We already generated this before, so just grab it from Redis
        data = gzip.decompress(CACHE.get(hash))  # type: ignore
        im = BytesIO(data)

        return Response(im.getvalue(), status=200, content_type='image/png')
    else:
        im = image.generate_image(poem, font, bg)
        # Give it an expiry of 6 hours to save space
        CACHE.set(str(hash), gzip.compress(im.getvalue()), ex=21600)

        return Response(im.getvalue(), status=200, content_type='image/png')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

if __name__ == '__main__':
    app.logger.info(
        f"Starting server on port {os.environ.get('PORT') or 7270}")
    app.logger.info(
        f"Using Redis at {os.environ.get('REDIS_URL') or 'redis://localhost:6379'}")
    app.run(port=int(os.environ.get('PORT') or 7270))
