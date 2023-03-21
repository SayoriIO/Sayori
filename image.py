from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
"""
    Shared code between all frontend. This handles image generation and text handling. At best, all shared code must be in this file
    to prevent any code duplication.
"""

PADDING = 60  # px, the spacing between the text and the edge of the image
# No need to worry about this, the offset is just to make the text look better
OFFSET = PADDING // 4
DEFAULT_FONT = 'm1'
DEFAULT_BG = Image.open('./backgrounds/' + 'poem_default.jpg')
FONTS = {
    'm1': ImageFont.truetype('./fonts/m1.ttf', 34),  # Monika
    's1': ImageFont.truetype('./fonts/s1.ttf', 34),  # Sayori
    'n1': ImageFont.truetype('./fonts/n1.ttf', 28),  # Natsuki
    'y1': ImageFont.truetype('./fonts/y1.ttf', 32),  # Yuri (Normal)
    'y2': ImageFont.truetype('./fonts/y2.ttf', 40),  # Yuri (Fast)
    'y3': ImageFont.truetype('./fonts/y3.ttf', 18)  # Yuri (Obsessed)
}

BACKGROUNDS = {
    'default': 'default',
    'y2': 'y2',
    'y3': 'y3'
}


def break_text(text: str, font: str, max_width: int):
    fnt: ImageFont.FreeTypeFont = FONTS.get(font)  # type: ignore
    word_list = text.split(' ')
    tmp = ''
    wrapped = []

    # Iterates through all the words, and if the width of a tempory variable and the word is larger than the max width,
    # the string is appended to a list, and the string is set to the word plus a space, otherwise the word is just added
    # to the temporary string with a space.
    for word in word_list:
        if fnt.getsize(tmp + word)[0] > max_width and fnt.getsize(word)[0] <= max_width:
            # Splits the line along all newlines, in order to properly obey them.
            tmp2 = tmp.strip().split('\n')

            wrapped.append(tmp2[0])

            # If more than one user-formatted line exists, iterate through all but the last one,
            # and then set tmp as the last line plus the new word.
            if tmp2[1:]:
                for line in tmp2[1:-1]:
                    wrapped.append(line)

                tmp = tmp2[-1] + ' ' + word + ' '
            else:
                tmp = word + ' '
        elif fnt.getsize(word)[0] > max_width:
            # Handle stupidly long words.
            for char in word:
                if fnt.getsize(tmp + char)[0] > max_width:
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


def generate_image(poem: str, font: str, bg: str) -> BytesIO:
    img = Image.open(f'./backgrounds/poem_{bg}.jpg')
    fnt = FONTS.get(font)
    draw = ImageDraw.Draw(img)

    b = BytesIO()
    poem = break_text(poem, font, img.width - PADDING * 2 + OFFSET)
    height = max(img.height, draw.textsize(poem, fnt)[1] + PADDING * 2)

    if height > img.height:
        img = img.resize((img.width, height), Image.BICUBIC)
        draw = ImageDraw.Draw(img)

    draw.text((PADDING-OFFSET, PADDING), poem, '#000000', fnt)
    img.save(b, 'png')
    b.seek(0)

    return b
