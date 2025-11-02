import streamlit as st
import requests
from bs4 import BeautifulSoup
import base64
from io import StringIO

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
            elem.decompose()
    
    return str(soup)

def create_download_link(content, filename):
    """
    Membuat link download untuk konten
    """
    # Encode konten ke base64
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

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
    4. Menyediakan link untuk mengakses file
    """)
    
    url = st.text_input(
        "Masukkan URL:",
        placeholder="https://example.com",
        value="https://www.persebaya.id"
    )
    
    if st.button("📥 Proses dan Buat File TXT", type="primary"):
        if not url:
            st.error("⚠️ Silakan masukkan URL terlebih dahulu!")
            return
        
        try:
            with st.spinner("Sedang memproses..."):
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                cleaned_content = clean_html_content(response.text)
                
                # Generate nama file
                domain = url.split('//')[-1].split('/')[0].replace('.', '_')
                filename = f"cleaned_{domain}.txt"
                
                # Buat link download
                download_link = create_download_link(cleaned_content, filename)
                
                st.session_state.cleaned_content = cleaned_content
                st.session_state.original_content = response.text
                st.session
