from tugasstrukdis.sidebarui import set_sidebar_background
from tugasstrukdis.parser import *
from tugasstrukdis.graph import Graph
import streamlit as st
import graphviz
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Java Code Visualizer", layout="wide")

try:
    set_sidebar_background("./assets/bluewpp.jpg")
except FileNotFoundError:
    pass
with (
    st.sidebar
):  # menggunakan sidebar untuk mengelompokan submit dan textfield di bagian kiri
    st.header("Upload/Tulis kode java kamu")
    uploaded_file = st.file_uploader(
        "**Pilih file (java)**", type=["java"]
    )  # membatasi agar file yang dapat diupload hanya bertipe java
    file_ada = uploaded_file is not None  # boolean jika file ada atau tidak ada
    if file_ada:  # jika ada
        # Menampilkan informasi file
        st.success(f" File berhasil diterima: {uploaded_file.name}")

        # Menampilkan detail ukuran file
        st.write(f"Ukuran file: {uploaded_file.size} bytes")
        stringio = uploaded_file.getvalue().decode("utf-8")
        java_code = stringio
        st.markdown("---")  # pembatas agar rapi

    # TEXT FIELD
    user_text = st.text_area(  # text field untuk copy paste code
        "**Paste kode java:**",
        height=150,
        disabled=file_ada,  # jika ada file maka textfield ini di disabeld
        placeholder="public class Main{...}",
    )
    if not file_ada:
        java_code = user_text
    # Logika untuk mengatur  submit bisa di enabled /disabled saat file ada maka textfield di disabled dan begitu sebaliknya

    tombol_submit = st.button("Submit", type="primary")


# ----- UI Main (Node)
if tombol_submit:
    if not java_code.strip():
        st.warning("Silahkan upload file/ketik code terlebih dahulu")
    else:
        st.header("Hasil Visualisasi Node")

        # panggil method analyze java code
        hasil = JavaCode(java_code)
        classes = hasil.classes
        if not classes:
            st.info("Tidak ditemukan")
            # tampilkan hasil
        for cls in classes:
            with st.expander(f"Class {cls.name}", expanded=True):
                cols = st.columns(2)

                for idx, method in enumerate(cls.methods):
                    col = cols[idx % 2]
                    with col:
                        st.subheader(method.name)

                        matrix = method.interference_matrix
                        if method.variables:
                            graph = Graph(method.interference_matrix)
                            st.info(
                                f"**Chromatic Number (Min Register): {graph.get_chromatic_number()}**"
                            )
                            st.caption(
                                "Warna yang berbeda menandakan variabel harus disimpan di register memori yang berbeda."
                            )
                            st.pyplot(graph.get_figure())
                            with st.popover("Lihat Matriks Interferensi"):
                                st.dataframe(pd.DataFrame(matrix).astype(bool))
                        else:
                            st.caption("Tidak ada variabel lokal.")
