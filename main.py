"""
DDLC-style poem generator written in Python, replacing the original Lua one by FiniteReality.
Created by Ovyerus (https://github.com/Ovyerus) and licensed under the MIT License.
"""
import os
import json
import textwrap
import asyncio

from io import BytesIO
from aiohttp import web
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor

"""
API Overview
------------

There are two accepted parameters, `poem` and `font`.
`poem` is the only required parameter, and specifies the content of the poem to generate.
`font` is optional, and if it is not a supported font, it will default to DEFAULT_FONT (usually `m1`).
Parameters can either be sent by a JSON body, or by a query string (?poem=Hello%20world&font=y1)

Requests can either be a GET or a POST, with the former being allowed to support browsers.
Both methods of submitting data are supported with both methods, however most things that send a GET will only allow the query string method (as far as I am aware).
"""

PADDING = 100 # px
DEFAULT_FONT = 'm1'
DEFAULT_BG = Image.open('./backgrounds/poem.jpg')

# Cache the fonts and backgrounds.

FONTS = {
    'm1': ImageFont.truetype('./fonts/m1.TTF', 34), # Monika
    's1': ImageFont.truetype('./fonts/s1.ttf', 34), # Sayori
    'n1': ImageFont.truetype('./fonts/n1.ttf', 28), # Natsuki
    'y1': ImageFont.truetype('./fonts/y1.ttf', 32), # Yuri (Normal)
    'y2': ImageFont.truetype('./fonts/y2.ttf', 40), # Yuri (Fast)
    'y3': ImageFont.truetype('./fonts/y3.ttf', 18) # Yuri (Obsessed)
}

BACKGROUNDS = {
    'y2': Image.open('./backgrounds/poem_y1.jpg'),
    'y3': Image.open('./backgrounds/poem_y2.jpg')
}

loop = asyncio.get_event_loop()
executor = ThreadPoolExecutor(max_workers=20)

# copied/stolen and adapted from code in Kitchen Sink
def break_text(text, font, max_width):
        # Split all text by newlines to begin with
        text = text.split("\n")
        # Just pick an arbitrary number as the maximum character number
        clip = int(max_width / 5)

        # create empty list to populate
        ret = []

        # loop through each line
        for t in text:
            temp = [t] # set default output (no further lines split)
            w, h = font.getsize(t) # get width of current line (height is discarded)
            # iterate through smaller and smaller character limits until all text fits
            while w > max_width:
                clip -= 1
                temp = textwrap.wrap(t, width=clip) # wrap text with set character limit
                w = max(font.getsize(m)[0] for m in temp) # get width of longest line

            ret += temp # add output to returning variable
        
        return "\n".join(ret)

def gen_img(poem, font, bg):
    draw = ImageDraw.Draw(bg)

    b = BytesIO()
    poem = break_text(poem, font, bg.width - PADDING * 2).replace('\u2426', '\n\n')
    height = max(bg.height, draw.textsize(poem, font)[1] + PADDING * 2)

    if height > bg.height:
        bg = bg.resize((bg.width, height), Image.BICUBIC)
        draw = ImageDraw.Draw(bg)

    draw.text((PADDING , PADDING), poem, '#000000', font)
    bg.save(b, 'png')
    b.seek(0)

    return b

async def handle_request(req):
    body = await req.text()
    is_json = True

    if not body:
        body = req.query
        is_json = False

    if not body:
        return web.Response(status=400, text='{"error": "No body or query string.", "code": 0}', content_type='application/json')

    if is_json:
        body = json.loads(body)

    if 'poem' not in body:
        return web.Response(status=400, text='{"error": "Missing required field: `poem`.", "code": 1}', content_type='application/json')

    if type(body['poem']) is not str:
        return web.Response(status=400, text='{"error": "Field `poem` is not a string.", "code": 2}',
                            content_type='application/json')

    if not body['poem']:
        return web.Response(status=400, text='{"error": "Field `poem` is empty.", "code": 3}', content_type='application/json')

    if 'font' in body and body['font'] not in FONTS:
        return web.Response(status=400,
                            text='{{"error": "Unsupported font. Supported fonts are: \\"{}\\"", "code": 4}}'.format('\\", \\"'.join(FONTS.keys())),
                            content_type='application/json')

    poem = body['poem'].replace('\r', '').replace('\n', '\u2426')
    _font = body.get('font', DEFAULT_FONT)

    bg = BACKGROUNDS.get(_font, DEFAULT_BG).copy()
    font = FONTS[_font]

    res = await loop.run_in_executor(executor, gen_img, poem, font, bg)

    return web.Response(body=res, content_type='image/png')

app = web.Application()

app.router.add_post('/generate', handle_request)
app.router.add_get('/generate', handle_request)

print('Loading poem server')
web.run_app(app, port=os.environ.get('PORT', 8080))
