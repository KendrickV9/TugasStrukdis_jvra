import streamlit as st
import graphviz 
from tugasstrukdis.sidebarui import set_sidebar_background
from tugasstrukdis.__init__ import analyze_java_code
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
def create_interference_graph(method_name, variables, matrix):
    """
    Membuat Graph Interferensi menggunakan NetworkX.
    - Node: Variabel
    - Edge: Jika variabel saling interferensi (hidup bersamaan)
    - Warna: Hasil algoritma Graph Coloring (Greedy)
    """
    G = nx.Graph()
    
    # 1. Tambahkan Node (Variabel)
    # Kita menggunakan nama variabel sebagai ID node
    var_map = {v.name: v for v in variables} # Helper untuk akses info variabel
    for var in variables:
        G.add_node(var.name, type=var.type)

    # 2. Tambahkan Edge berdasarkan Matrix
    # Kita gunakan loop index (i, j) agar aman untuk List maupun Dict
    num_vars = len(variables)
    
    # Cek tipe data matrix untuk menentukan cara akses
    is_dict = isinstance(matrix, dict)
    
    for i in range(num_vars):
        for j in range(i + 1, num_vars): # i + 1 untuk menghindari duplikasi & self-loop
            name_i = var_names[i]
            name_j = var_names[j]
            
            connected = False
            
            # Logika akses jika matrix adalah Dictionary {name: {name: bool}}
            if is_dict:
                # Coba akses aman (get)
                row = matrix.get(name_i, {})
                if isinstance(row, dict):
                    connected = row.get(name_j, False)
            
            # Logika akses jika matrix adalah List of Lists [[bool, bool], ...]
            elif isinstance(matrix, list):
                try:
                    connected = matrix[i][j]
                except IndexError:
                    connected = False # Hindari error jika ukuran matrix beda
            
            # Jika terhubung (Interferensi), buat garis (Edge)
            if connected:
                G.add_edge(name_i, name_j)

    # 3. Algoritma Graph Coloring (Greedy)
    coloring_result = nx.coloring.greedy_color(G, strategy='largest_first')
    chromatic_number = max(coloring_result.values()) + 1 if coloring_result else 0

    return G, coloring_result, chromatic_number

def plot_networkx_graph(G, coloring_result):
    """
    Fungsi helper untuk menggambar graph NetworkX ke Matplotlib Figure
    agar bisa dirender oleh Streamlit.
    """
    # Palette warna (Hex codes) untuk membedakan register
    colors_palette = [
        '#FF9999', '#66B2FF', '#99FF99', '#FFCC99', 
        '#c2c2f0', '#ffb3e6', '#c2f0c2', '#ff6666'
    ]
    
    # Mapping warna node berdasarkan hasil coloring
    node_colors = []
    for node in G.nodes():
        # Ambil index warna dari hasil algo (default 0 jika tidak ada)
        color_idx = coloring_result.get(node, 0)
        # Pilih warna dari palette (gunakan modulo jika warna habis)
        color = colors_palette[color_idx % len(colors_palette)]
        node_colors.append(color)

    # Setup Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Layout graph (Spring layout biasanya paling rapi untuk graph relasi)
    pos = nx.spring_layout(G, seed=42) 

    # Gambar Graph
    nx.draw(
        G, pos, 
        with_labels=True, 
        node_color=node_colors, 
        edge_color="gray", 
        width=1.5, 
        node_size=2000, 
        font_size=10, 
        font_weight="bold",
        ax=ax
    )
    
    ax.set_title("Interference Graph & Register Allocation", fontsize=15)
    return fig

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Java Code Visualizer", layout="wide")

try:
   set_sidebar_background("./assets/bluewpp.jpg")
except FileNotFoundError:
   pass
with st.sidebar:#menggunakan sidebar untuk mengelompokan submit dan textfield di bagian kiri
 st.header("Upload/Tulis kode java kamu")
 uploaded_file = st.file_uploader("**Pilih file (java)**", type=['java']) #membatasi agar file yang dapat diupload hanya bertipe java
 file_ada=uploaded_file is not None#boolean jika file ada atau tidak ada
 if file_ada:#jika ada
    # Menampilkan informasi file
    st.success(f" File berhasil diterima: {uploaded_file.name}")
    
    # Menampilkan detail ukuran file
    st.write(f"Ukuran file: {uploaded_file.size} bytes")
    stringio=uploaded_file.getvalue().decode("utf-8")
    java_code=stringio
    st.markdown("---")#pembatas agar rapi
   
 # TEXT FIELD
 user_text=st.text_area(#text field untuk copy paste code
   "**Paste kode java:**", 
     height=150,
     disabled=file_ada,#jika ada file maka textfield ini di disabeld
     placeholder="public class Main{...}"
   )
 if not file_ada:
   java_code=user_text
 #Logika untuk mengatur  submit bisa di enabled /disabled saat file ada maka textfield di disabled dan begitu sebaliknya
 
 tombol_submit=st.button("Submit",type="primary")


# ----- UI Main (Node)
if tombol_submit:
   if not java_code.strip():
      st.warning("Silahkan upload file/ketik code terlebih dahulu")
   else:
      st.header("Hasil Visualisasi Node")

      # panggil method analyze java code
      hasil=analyze_java_code(java_code)
      if "error" in hasil:
         st.error(f"Error Parsing: {hasil["error"]}")
      else:
         data_classes=hasil["data"]

         if not data_classes:
            st.info("Tidak ditemukan")
            #tampilkan hasil
         for cls in data_classes:
            if not cls:continue
            with st.expander(f"Class {cls["class_name"]}",expanded=True):
               cols=st.columns(2)

               for idx , method in enumerate(cls['methods']):
                  col=cols[idx%2]
                  with col:
                     st.subheader(f"{method["method_name"]}")
                     
                     vars_list=method["variables"]
                     matrix= method.get("matrix",{})
                     if vars_list:
                       try:
                        G, coloring, min_registers = create_interference_graph(method['method_name'], vars_list, matrix)
              
                    # 2. Tampilkan Info Register
                        st.info(f"**Chromatic Number (Min Register): {min_registers}**")
                        st.caption("Warna yang berbeda menandakan variabel harus disimpan di register memori yang berbeda.")

                        # 3. Render Plot menggunakan Matplotlib
                        fig_graph = plot_networkx_graph(G, coloring)
                        st.pyplot(fig_graph)

                        # 4. Tampilkan Matriks Interferensi (Opsional)
                        with st.popover("Lihat Matriks Interferensi"):
                            st.dataframe(pd.DataFrame(matrix).astype(bool))
                       except Exception as e:
                          st.error(f"Gagal membuat graph: {e}")
                     else:
                        st.caption("Tidak ada variabel lokal.")