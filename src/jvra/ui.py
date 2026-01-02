import sys
import os


# 1. Ambil lokasi folder tempat ui.py berada (yaitu folder 'jvra')
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Ambil folder di atasnya (yaitu folder 'src')
src_dir = os.path.dirname(current_dir)

# 3. Masukkan folder 'src' ke sistem pencarian Python
# Supaya python bisa mengenali perintah "from jvra..."
sys.path.append(src_dir)
# -----------------------------------
from jvra.sidebarui import set_sidebar_background
from jvra.parser import JavaCode, JavaClass, JavaMethod
from jvra.graph import Graph
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import javalang


def load_sidebar() -> None:
    try:
        set_sidebar_background("./assets/bluewpp.jpg")
    except FileNotFoundError:
        pass
    with st.sidebar:
        # menggunakan sidebar untuk mengelompokan submit dan textfield di bagian kiri
        st.header("Upload/Tulis kode Java")

        # membatasi agar file yang dapat diupload hanya bertipe java
        uploaded_file = st.file_uploader("**Pilih file (java)**", type=["java"])

        file_ada = uploaded_file is not None  # boolean jika file ada atau tidak ada
        java_code_input = ""
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
            placeholder="public class Main { ... }",
        )
        if not file_ada:
            java_code = user_text
        # Logika untuk mengatur  submit bisa di enabled /disabled saat file ada maka textfield di disabled dan begitu sebaliknya

        tombol_submit = st.button("Submit", type="primary", width="stretch")

    if tombol_submit:
        load_class_analysis(java_code)


def load_method_analysis(java_method: JavaMethod, parsed_code: JavaCode) -> None:
    col_snippet, col_graph = st.columns(2)
    with col_snippet:
        st.code(
            parsed_code.get_snippet(java_method.start_line, java_method.end_line),
            language="java",
            line_numbers=True,
        )

    with col_graph:
        if not java_method.variables:
            st.info("Method tidak menggunakan variabel lokal")
            return

        matrix = java_method.interference_matrix
        graph = Graph(java_method.interference_matrix)
        st.pyplot(graph.figure)

        register_map: dict[str, str] = {
            var: f"r{reg}" for var, reg in graph.colors.items()
        }  # ambil dict
        df_registers = pd.DataFrame(
            list(register_map.items()),
            columns=["Nama Variabel", "Register ID (Warna)"],
        )  # buat tabelnya dan isi

        # sorting dengan valuenya
        df_registers = df_registers.sort_values(by="Register ID (Warna)")

    st.divider()
    st.markdown(
        "<h4 style='text-align: center;'>Alokasi Register</h4>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        df_registers,
        hide_index=True,  # Sembunyikan index angka 0,1,2 di kiri tabel
    )
    with st.popover("Lihat Matriks Interferensi"):
        st.dataframe(pd.DataFrame(matrix).astype(bool))


def load_class_analysis(java_code: str) -> None:
    java_code = java_code.strip()
    if not java_code:
        st.warning("Silahkan upload file/ketik code terlebih dahulu")
        return

    try:
        parsed_code = JavaCode(java_code)
    except javalang.parser.JavaSyntaxError as e:
        st.error(f"Syntax error: {e.at}")
        return

    if not parsed_code.classes:
        st.info("Tidak ada kelas Java")
        return

    for i, java_class in enumerate(parsed_code.classes):
        with st.expander(f"class {java_class.name}", expanded=True):
            if not java_class.methods:
                st.info(f"kelas '{java_class.name}' tidak memiliki method")
                continue

            tabs = st.tabs(list(map(lambda m: f"{m.name}()", java_class.methods)))
            for method in java_class.methods:
                load_method_analysis(method, parsed_code)


def main() -> None:
    if "__streamlitmagic__" not in globals():
        from streamlit.web.bootstrap import run

        run(__file__, False, [], {})
    else:
        # ----- UI Main (Node)
        st.set_page_config(
            page_title="Java Code Visualizer",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        load_sidebar()


if __name__ == "__main__":
    main()
