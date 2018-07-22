"""
DDLC-style poem generator written in Python, replacing the original Lua one by FiniteReality.
Created by Ovyerus (https://github.com/Ovyerus) and Capuccino (https://github.com/sr229) and licensed under the MIT License.
"""
import os
import json
import asyncio
import yaml
import shutil
import hashlib
import pickle
import redis

from io import BytesIO, StringIO
from aiohttp import web
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# API Overview
# ------------

# There are two accepted parameters, `poem` and `font`.
# `poem` is the only required parameter, and specifies the content of the poem to generate.
# `font` is optional, and if it is not a supported font, it will default to DEFAULT_FONT (usually `m1`).
# Parameters can either be sent by a JSON body, or by a query string (?poem=Hello%20world&font=y1)

# Requests can either be a GET or a POST, with the former being allowed to support browsers.
# Both methods of submitting data are supported with both methods,
# however most things that send a GET will only allow the query string method (as far as I am aware).


def is_url(url):
    res = urlparse(url)
    return (res.scheme and res.scheme in ['https', 'http']) and res.netloc


def break_text(text, font, max_width):
    word_list = text.split(' ')
    tmp = ''
    wrapped = []

    # Iterates through all the words, and if the width of a tempory variable and the word is larger than the max width,
    # the string is appended to a list, and the string is set to the word plus a space, otherwise the word is just added
    # to the temporary string with a space.
    for word in word_list:
        if font.getsize(tmp + word)[0] > max_width and font.getsize(word)[0] <= max_width:
            tmp2 = tmp.strip().split('\n')  # Splits the line along all newlines, in order to properly obey them.

            wrapped.append(tmp2[0])

            # If more than one user-formatted line exists, iterate through all but the last one,
            # and then set tmp as the last line plus the new word.
            if tmp2[1:]:
                for line in tmp2[1:-1]:
                    wrapped.append(line)

                tmp = tmp2[-1] + ' ' + word + ' '
            else:
                tmp = word + ' '
        elif font.getsize(word)[0] > max_width:
            # Handle stupidly long words.
            for char in word:
                if font.getsize(tmp + char)[0] > max_width:
                    wrapped.append(tmp.strip())
                    tmp = char
                else:
                    tmp += char

            tmp += ' '
        else:
            tmp += word + ' '

    # Add remaining words
    if tmp:
        wrapped.append(tmp.strip())

    return '\n'.join(wrapped)


def gen_img(poem, font, bg):
    draw = ImageDraw.Draw(bg)

    b = BytesIO()
    poem = break_text(poem, font, bg.width - PADDING * 2)
    height = max(bg.height, draw.textsize(poem, font)[1] + PADDING * 2)

    if height > bg.height:
        bg = bg.resize((bg.width, height), Image.BICUBIC)
        draw = ImageDraw.Draw(bg)

    draw.text((PADDING, PADDING), poem, '#000000', font)
    bg.save(b, 'png')
    b.seek(0)

    return b


@web.middleware
async def cors_middleware(req, handler):
    resp = await handler(req)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return resp


# Just return a 200 to allow option requests to pass through.
# The CORS middleware above sets the appropriate headers.
async def handle_options(req):
    return web.Response(status=200)


async def handle_request(req):
    body = await req.text()
    is_json = True

    if not body:
        body = req.query
        is_json = False

    if not body:
        return web.json_response({'error': 'No body or query string.', 'code': 0}, status=400)

    if is_json:
        body = json.loads(body)

    if 'poem' not in body:
        return web.json_response({'error': 'Missing required field: "poem".', 'code': 1}, status=400)

    if not isinstance(body['poem'], str):
        return web.json_response({'error': 'Field "poem" is not a string.', 'code': 2}, status=400)

    if not body['poem']:
        return web.json_response({'error': 'Field "poem" is empty.', 'code': 3}, status=400)

    if 'font' in body and body['font'] not in FONTS:
        return web.json_response({'error': 'Unsupported font.', 'valid_fonts': FONTS.keys(), 'code': 4}, status=400)

    poem = body['poem'].replace('\r', '')
    _font = body.get('font', DEFAULT_FONT)
    hashed = hashlib.md5((body['poem'] + _font).encode('utf8')).hexdigest()
    hashed_path = f'./poems/{hashed}.png'
    
    # Save to redis
    if CACHE:
      output = StringIO()
      im = Image.open(f'./poems/{hashed}.png')
      im.save(output, format=im.format)
      redis.set(f'poem:{hashed}', output.getvalue(), ex=259200)

    if os.path.exists(hashed_path) and CACHE:
        res_url = f'{RESULT_URL}/poems/{hashed}.png'
        return web.json_response({'id': hashed, 'url': res_url})

    bg = BACKGROUNDS.get(_font, DEFAULT_BG).copy()
    font = FONTS[_font]

    res = await loop.run_in_executor(executor, gen_img, poem, font, bg)

    if CACHE:
        # let's check if this exists
        # If not, we create it from Redis Cache
        if redis.exists(f'poem:{hashed}'):
           with redis.get(f'poem:{hashed}') as data:
               if os.path.exists(hashed_path):
                  print('ignoring secondary cache recovery.')
                else:
                  open(hashed_path)
                  data.write(data)
                  data.close()
        # The same image might've been generated in the mean time.
        # Check *just* in case.
        if not os.path.exists(hashed_path):
            with open(hashed_path, 'wb') as f:
                shutil.copyfileobj(res, f, length=131072)
        
        res_url = f'{RESULT_URL}/poems/{hashed}.png'
        return web.json_response({'id': hashed, 'url': res_url})

    return web.json_response(body=res, content_type='image/png')

# If the config file is not present, clone the example file if there aren't all the environment vars.
if not os.path.exists('./config.yaml'):
    if all(x in os.environ for x in ('DEFAULT_FONT', 'DEFAULT_BG', 'PADDING', 'CDN', 'RESULT_URL', 'CACHE', 'PORT')):
        print('All config options have been detected as environment variables. Loading...')

        config = {
            'padding': int(os.environ['PADDING']),
            'default_font': os.environ['DEFAULT_FONT'],
            'default_bg': os.environ['DEFAULT_BG'],
            'cdn': os.environ['CDN'],
            'redis_host': os.environ['REDIS_URL' or 'REDISCLOUD_URL'],
            'result_url': os.environ['RESULT_URL'],
            'cache': True if os.environ['CACHE'].lower() == 'true' else False,
            'port': int(os.environ['PORT'])
        }
    else:
        print('Cloning default configuration file.')
        shutil.copyfile('./config.example.yaml', './config.yaml')

# Load config and assign to variables.
if os.path.exists('./config.yaml'):
    with open('./config.yaml') as c:
        config = yaml.load(c)

PADDING = config['padding']  # px
DEFAULT_FONT = config['default_font']
DEFAULT_BG = Image.open('./backgrounds/' + config['default_bg'])

CACHE = config['cache']
RESULT_URL = config['result_url']  # If there is a CDN specified, this gets overwritten.

# If the cdn option is a URL, set RESULT_URL to it,
# otherwise if there is an environment variable that exists with the value, set that instead.
if is_url(config['cdn']):
    RESULT_URL = config['cdn']
    CACHE = True
elif os.environ.get(config['cdn']):
    RESULT_URL = os.environ[config['cdn']]
    CACHE = True
elif os.environ.get(config['redis_host']):
    REDIS_URL = os.environ[config['redis_host']]

# Cache the fonts and backgrounds.
FONTS = {
    'm1': ImageFont.truetype('./fonts/m1.TTF', 34),  # Monika
    's1': ImageFont.truetype('./fonts/s1.ttf', 34),  # Sayori
    'n1': ImageFont.truetype('./fonts/n1.ttf', 28),  # Natsuki
    'y1': ImageFont.truetype('./fonts/y1.ttf', 32),  # Yuri (Normal)
    'y2': ImageFont.truetype('./fonts/y2.ttf', 40),  # Yuri (Fast)
    'y3': ImageFont.truetype('./fonts/y3.ttf', 18)  # Yuri (Obsessed)
}

BACKGROUNDS = {
    'y2': Image.open('./backgrounds/poem_y1.jpg'),
    'y3': Image.open('./backgrounds/poem_y2.jpg')
}

BEVERAGE_TYPES = ('chai', 'oolong', 'green', 'herbal', 'black', 'yellow')

loop = asyncio.get_event_loop()
executor = ThreadPoolExecutor(max_workers=20)
app = web.Application(middlewares=[cors_middleware])
redis = redis.StrictRedis(host=config['redis_host'])


if not os.path.exists('./poems'):
    os.mkdir('./poems')

app.router.add_post('/generate', handle_request)
app.router.add_get('/generate', handle_request)
app.router.add_route('OPTIONS', '/generate', handle_options)
app.router.add_static('/poems', './poems')

print('Loading poem server')
web.run_app(app, port=int(os.environ.get('PORT', config['port'])))
