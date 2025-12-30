from tugasstrukdis.sidebarui import set_sidebar_background
from tugasstrukdis.parser import *
from tugasstrukdis.graph import Graph
import streamlit as st
import graphviz
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


# --- KONFIGURASI HALAMAN ---
def configure_page() -> None:
    st.set_page_config(page_title="Java Code Visualizer", layout="wide")
    try:
        set_sidebar_background("./assets/bluewpp.jpg")
    except FileNotFoundError:
        pass


def load_page() -> None:
    # Gunakan sidebar untuk mengelompokan submit dan textfield di bagian kiri
    with st.sidebar:
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
        st.set_page_config(initial_sidebar_state="collapsed")
        if not java_code.strip():
            st.warning("Silahkan upload file/ketik code terlebih dahulu")
        else:
            st.header("Hasil Visualisasi Node")

            # panggil method analyze java code
            hasil = JavaCode(java_code)
            classes = hasil.classes
            if not classes:
                st.info("Tidak ada kelas")
                # tampilkan hasil
            for cls in classes:
                with st.expander(f"Class {cls.name}", expanded=True):
                    if not cls.methods:
                        st.warning("Tidak ada method.")
                        continue

                    cols = st.columns(2)

                    for idx, method in enumerate(cls.methods):
                        col = cols[idx % 2]
                        with col:
                            st.subheader(f"{method.name}()")

                            matrix = method.interference_matrix
                            if method.variables:
                                graph = Graph(method.interference_matrix)
                                st.info(
                                    f"**Chromatic Number (Min Register): {graph.get_chromatic_number()}**"
                                )
                                st.caption(
                                    "Warna yang berbeda menandakan variabel harus disimpan di register memori yang berbeda."
                                )
                                register_map = graph.get_colors()  # ambil dict
                                df_registers = pd.DataFrame(
                                    list(register_map.items()),
                                    columns=["Nama Variabel", "Register ID (Warna)"],
                                )  # buat tabelnya dan isi

                                # sorting dengan valuenya
                                df_registers = df_registers.sort_values(
                                    by="Register ID (Warna)"
                                )

                                st.write("### Detail Pembagian Register")
                                st.dataframe(
                                    df_registers,
                                    use_container_width=True,
                                    hide_index=True,  # Sembunyikan index angka 0,1,2 di kiri tabel
                                )
                                st.pyplot(graph.get_figure())
                                with st.popover("Lihat Matriks Interferensi"):
                                    st.dataframe(pd.DataFrame(matrix).astype(bool))
                            else:
                                st.caption("Tidak ada variabel lokal.")


def main():
    if "__streamlitmagic__" not in globals():
        from streamlit.web.bootstrap import run

        run(__file__, False, [], {})
    else:
        configure_page()
        load_page()


if __name__ == "__main__":
    main()
