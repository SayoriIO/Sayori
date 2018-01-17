# Sayori

A HTTP-based poem generator for Monika.  
At least Python 3.6 is required to run the server.  
All dependencies are specified in `requirements.txt`.

## Setup

Some files are needed in order for Sayori to run correctly, and they must be extracted from the game files of Doki Doki Literature Club.

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

If you can't be assed to download the game (if you haven't already) and extract the assets, there are some alternative methods to get these files.

1. You can download and extract the two folders inside this zip archive https://owo.whats-th.is/d7c9fe.zip  
2. If you can't even be assed to do that, you can run either of the `get-resources` scripts, depending on your system (`.bat` for Windows, `.sh` for Linux).
 - NOTE: The `.sh` script requires `unzip` to be installed on the system. This can be installed with the respective package manager of your distribution.

And if you even can't be arsed to do anything, we made a Heroku button especially for deploying your own version of Sayori.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)