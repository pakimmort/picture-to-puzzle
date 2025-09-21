import streamlit as st
from PIL import Image, ImageDraw
import io
import random

def make_puzzle(img, rows=4, cols=6):
    w, h = img.size
    pw, ph = w // cols, h // rows
    pieces = []
    for r in range(rows):
        for c in range(cols):
            box = (c*pw, r*ph, (c+1)*pw, (r+1)*ph)
            piece = img.crop(box)
            pieces.append(piece)
    return pieces

st.title("🧩 Jigsaw Puzzle Generator")

uploaded_file = st.file_uploader("Upload an image", type=["jpg","png","jpeg"])
if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Original Image", use_column_width=True)

    rows = st.slider("Rows", 2, 10, 4)
    cols = st.slider("Cols", 2, 10, 6)

    if st.button("Generate Puzzle"):
        pieces = make_puzzle(img, rows, cols)
        st.write(f"Generated {len(pieces)} puzzle pieces")

        # Display pieces
        for piece in pieces:
            st.image(piece)

        # Save all pieces in a zip
        buf = io.BytesIO()
        with io.BytesIO() as output:
            img.save(output, format="PNG")
            st.download_button(
                "Download Puzzle (not shuffled)",
                output.getvalue(),
                "puzzle.png",
                "image/png"
            )
