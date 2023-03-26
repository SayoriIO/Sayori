#!/usr/bin/env python3
import os
from flask import Flask, Request, Response, request
import image

app = Flask(__name__)


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
    im = image.generate_image(poem, font, bg)

    return Response(im.getvalue(), status=200, content_type='image/png')

if __name__ == '__main__':
    app.logger.info(
        f"Starting server on port {os.environ.get('PORT') or 7270}")
    app.run(port=int(os.environ.get('PORT') or 7270))
