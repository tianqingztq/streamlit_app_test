import streamlit as st
# import pandas as pd

st.write("Hello")

from streamlit.components.v1 import html

with open("code/index.html", "r") as f:
    html_content = f.read()

with open("code/css/styles.css", "r") as css_file:
    css_content = css_file.read()

with open("code/js/script.js", "r") as js_file:
    js_content = js_file.read()


html(
    f"<style>{css_content}</style>\n{html_content}<script>{js_content}</script>", 
    height=1000, 
    width=1100,
    scrolling=True)