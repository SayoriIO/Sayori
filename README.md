<p align="center">
   <img alt="Sayori" src="./sayori.png">
</p>

# Sayori - render your prose/poems like it's Doki Doki Literature Club!
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y8Y6Y0W4)

Sayori allows you to add more flair to your poems or proses and render them in Doki Doki Literature Club's style, using Python's PIL module to generate images for you to share!

Sayori can generate images with the following parameters:

- The text (can be uploaded as a plaintext file as well if you fancy that!)
- Background Type (Normal, or Yuri (Obsession Level from 2-3))
- The characters' writing styles (Monika (by default), Sayori, Natsuki, Yuri (and her obsessed variants))

## Try it for yourself!
Sayori is hosted on [Streamlit!](https://sayori.streamlit.app/)

However, if you want to integrate the project to your application, a hosted API is available as well! You can find it [here](sayori.fly.dev). Documentation for the API version can be found [here](./WEBSERVER_API.md).

## Installation

Sayori requires a modern Python installation to work. It is recommended to use Python 3.6 or above. As for the dependencies, don't worry about that! It's provided in the requirements.txt file, so you can just run:

```bash
    $ pip install -r requirements.txt
```

To run the web application, simply run

```bash
   $ streamlit run streamlit_main.py
```

## Development

Sayori takes advantage of the Virtual Environments feature in Python. To develop for Sayori, you must make a venv first:

```bash
   $ python -m venv $(pwd)/.venv
```
Then finally activate your virtual environment

```bash
   $ source $(pwd)/.venv/bin/activate
```

This ensures a consistent environment regardless of your development environment settings. After switching to the new
virtual environment, simply follow the [Installation](#installation) instructions.

## Copyright

Copyright &copy; 2023 Ayase Minori. All Rights Reserved. Licensed under the MIT License. See [LICENSE](./LICENSE) for more information.

Assets used in this project are property of Team Salvato and are used for educational purposes only. No infringement intended.
