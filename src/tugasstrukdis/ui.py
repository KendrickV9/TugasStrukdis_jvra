import streamlit as st
st.set_page_config(page_title="")

with st.sidebar:#menggunakan sidebar untuk mengelompokan submit dan textfield di bagian kiri
 st.write("# Upload/Tulis kode java kamu ")
 uploaded_file = st.file_uploader("Pilih file (java)", type=['java']) #membatasi agar file yang dapat diupload hanya bertipe java
 file_ada=uploaded_file is not None#boolean jika file ada atau tidak ada
 if file_ada:#jika ada
    # Menampilkan informasi file
    st.success(f" File berhasil diterima: {uploaded_file.name}")
    
    # Menampilkan detail ukuran file
    st.write(f"Ukuran file: {uploaded_file.size} bytes")
    st.markdown("---")#pembatas agar rapi
   
 # TEXT FIELD
 user_text=st.text_area(#text field untuk copy paste code
   "Paste kode java:", 
     height=150,
     disabled=file_ada,#jika ada file maka textfield ini di disabeld
     placeholder="public class Main{...}"
   )
 #Logika untuk mengatur  submit bisa di enabled /disabled saat file ada maka textfield di disabled dan begitu sebaliknya
 siap_submit=file_ada or user_text
 tombol_submit=st.button("Submit",disabled=not siap_submit,type="primary")


    
   