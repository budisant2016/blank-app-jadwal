import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import tempfile
from urllib.parse import quote

def clean_html_content(html_content):
    """
    Membersihkan HTML dengan menghapus elemen-elemen tertentu
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Daftar elemen yang akan dihapus
    elements_to_remove = [
        {'name': 'div', 'class': 'container persebaya-nav'},
        {'name': 'div', 'class': 'row mt-4 mb-2'},
        {'name': 'form', 'action': 'https://www.persebaya.id/search/result'},
        {'name': 'div', 'class': 'row mt-4 pl-md-5 pr-md-5'},
        {'name': 'div', 'id': 'footer-top'}
    ]
    
    # Menghapus setiap elemen yang ditentukan
    for element in elements_to_remove:
        if 'class' in element:
            elements = soup.find_all(element['name'], class_=element['class'])
        elif 'id' in element:
            elements = soup.find_all(element['name'], id=element['id'])
        elif 'action' in element:
            elements = soup.find_all(element['name'], action=element['action'])
        
        for elem in elements:
            elem.decompose()  # Menghapus elemen dari pohon HTML
    
    return str(soup)

def save_txt_file(content, filename):
    """
    Menyimpan konten ke file TXT dan mengembalikan path
    """
    # Buat direktori temporary jika belum ada
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

def main():
    st.set_page_config(
        page_title="HTML Content Cleaner",
        page_icon="🧹",
        layout="wide"
    )
    
    st.title("🧹 HTML Content Cleaner")
    st.markdown("""
    Aplikasi ini akan:
    1. Membaca konten dari URL yang Anda masukkan
    2. Menghapus elemen-elemen HTML tertentu
    3. Menyimpan hasilnya ke file TXT
    4. Menampilkan URL file TXT untuk diakses
    """)
    
    # Input URL
    url = st.text_input(
        "Masukkan URL:",
        placeholder="https://example.com",
        value="https://www.persebaya.id"  # Default value
    )
    
    # Tampilkan elemen yang akan dihapus
    with st.expander("Elemen yang akan dihapus:"):
        st.code("""
        - <div class="container persebaya-nav">
        - <div class="row mt-4 mb-2">
        - <form action="https://www.persebaya.id/search/result" ...>
        - <div class="row mt-4 pl-md-5 pr-md-5">
        - <div id="footer-top" class="row align-items-center ...">
       
