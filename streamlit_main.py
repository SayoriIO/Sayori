import streamlit as st
import image

# Our header is a Markdown file so let's use that instead.
st.markdown(open("STREAMLIT_HEADER.md").read())

font = st.selectbox("Font", ["Monika", "Sayori", "Natsuki", "Yuri", "Yuri (Fast)", "Yuri (Obsessed)"])
background = st.selectbox("Background", ["Default", "Yuri (Fast)", "Yuri (Obsessed)"])

# Accept either a text file or direct input
uploaded_file = st.file_uploader("Choose a file", type="txt")
poem = st.text_area("Or paste your poem here", height=300)

# Translate the font style to their respective IDs. 
def fontName2ID(fnt):
    if fnt == "Monika":
        return "m1"
    elif fnt == "Sayori":
        return "s1"
    elif fnt == "Natsuki":
        return "n1"
    elif fnt == "Yuri":
        return "y1"
    elif fnt == "Yuri (Fast)":
        return "y2"
    elif fnt == "Yuri (Obsessed)":
        return "y3"
    else:
        return "m1"

def bgName2ID(bg):
    if bg == "Default":
        return "default"
    elif bg == "Yuri (Fast)":
        return "y1"
    elif bg == "Yuri (Obsessed)":
        return "y2"

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
