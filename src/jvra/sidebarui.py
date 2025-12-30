import base64
import streamlit as st

def set_sidebar_background(img_path):
    with open(img_path, "rb") as f:
        data=f.read()
    bin_str = base64.b64encode(data).decode()
    page_bg_img = f"""
    <style>
    [data-testid="stSidebar"] {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    # Inject CSS ke Streamlit
    st.markdown(page_bg_img, unsafe_allow_html=True)