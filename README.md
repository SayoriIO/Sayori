# ImageGenerator

A small utility tool to generate images for Monika.  
At least Python 3.5 is required to run the server.  
[Pillow](https://python-pillow.org/) is also required, and can be installed by running `pip3 install Pillow` (or equivalent thereof)

## Setup

In the `backgrounds` directory you must put three files:
- `poem_y1.jpg`, the background for any Yuri poem generated using Yuri's second font
- `poem_y2.jpg`, the background for any Yuri poem generated using Yuri's third font
- `poem.jpg`, the background for any other poem generated.

In the `fonts` directory you must put six files:
- `m1.ttf`, the font to use when generating one of Monika's poems
- `n1.ttf`, the font to use when generating one of Natsuki's poems
- `s1.ttf`, the font to use when generating one of Sayori's poems
- `y1.ttf`, the font to use when generating one of Yuri's normal poems
- `y2.ttf`, the font to use when generating one of Yuri's Act 2 poems
- `y3.ttf`, the font to use when generating one of Yuri's obsessed poems