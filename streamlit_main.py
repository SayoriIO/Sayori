import streamlit as st
import image

# SEO stuff
st.set_page_config(page_title="Sayori Poem Generator - Powered by Streamlit", page_icon="💖", layout="centered")

# Our header is a Markdown file so let's use that instead.
st.markdown(open("STREAMLIT_HEADER.md").read())

font_names = {
    "Monika": "m1",
    "Sayori": "s1",
    "Natsuki": "n1",
    "Yuri": "y1",
    "Yuri (Fast)": "y2",
    "Yuri (Obsessed)": "y3"
}

background_names = {
    "Default": "default",
    "Yuri (Fast)": "y1",
    "Yuri (Obsessed)": "y2"
}

font = st.selectbox("Font", list(font_names.keys()))
background = st.selectbox("Background", list(background_names.keys()))

# Accept either a text file or direct input
uploaded_file = st.file_uploader("Choose a file", type="txt")
poem = st.text_area("Or paste your poem here", height=300)

# Translate the font style to their respective IDs.
def fontName2ID(fnt):
    return font_names.get(fnt, "m1")

def bgName2ID(bg):
    return background_names.get(bg, "default")

if st.button("Generate"):
  # Don't do anything if all variables are empty
  if uploaded_file is None and poem == "":
    st.error("Error: No poem found!")
  else:
    if uploaded_file is not None:
        # Read the file as bytes.
        # File might be CRLF-encoded so we trim out the carriage returns as well.
        contents = uploaded_file.read().decode("utf-8").replace('\r', '')
        img = image.generate_image(contents, fontName2ID(font), bgName2ID(background)) # type: ignore
        st.image(img, caption="Your poem", use_column_width=True)
        st.download_button("Download", img, "poem.png")
    else:
        img = image.generate_image(poem, fontName2ID(font), bgName2ID(background)) # type: ignore
        st.image(img, caption="Your poem", use_column_width=True)
        st.download_button("Download", img, "poem.png")
