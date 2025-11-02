import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

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

def save_to_txt(content, filename):
    """
    Menyimpan konten ke file txt
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

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
    3. Menyimpan hasilnya ke file TXT yang dapat diunduh
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
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Ambil dan Bersihkan Konten", type="primary"):
            if not url:
                st.error("⚠️ Silakan masukkan URL terlebih dahulu!")
                return
            
            try:
                with st.spinner("Sedang mengambil dan membersihkan konten..."):
                    # Headers untuk menghindari blokir
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    # Ambil konten dari URL
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    # Bersihkan konten HTML
                    cleaned_content = clean_html_content(response.text)
                    
                    # Simpan ke session state
                    st.session_state.cleaned_content = cleaned_content
                    st.session_state.original_content = response.text
                    
                    st.success("✅ Konten berhasil diambil dan dibersihkan!")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Gagal mengambil konten: {str(e)}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {str(e)}")
    
    with col2:
        if 'cleaned_content' in st.session_state:
            # Buat nama file berdasarkan URL
            domain = url.split('//')[-1].split('/')[0].replace('.', '_')
            filename = f"cleaned_{domain}.txt"
            
            # Simpan ke file
            file_path = save_to_txt(st.session_state.cleaned_content, filename)
            
            # Tampilkan preview
            with st.expander("📋 Preview Konten yang Sudah Dibersihkan"):
                st.text_area(
                    "Konten (pertama 2000 karakter):",
                    st.session_state.cleaned_content[:2000] + "..." if len(st.session_state.cleaned_content) > 2000 else st.session_state.cleaned_content,
                    height=200
                )
            
            # Download button
            st.download_button(
                label="📥 Download File TXT",
                data=st.session_state.cleaned_content,
                file_name=filename,
                mime="text/plain",
                help="Klik untuk mengunduh file TXT yang sudah dibersihkan"
            )
            
            # Tampilkan statistik
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Konten Asli", f"{len(st.session_state.original_content):,} chars")
            with col_stat2:
                st.metric("Setelah Dibersihkan", f"{len(st.session_state.cleaned_content):,} chars")
            with col_stat3:
                reduction = len(st.session_state.original_content) - len(st.session_state.cleaned_content)
                st.metric("Pengurangan", f"{reduction:,} chars")

    # Informasi tambahan
    st.markdown("---")
    st.markdown("""
    ### 📝 Cara Menggunakan:
    1. Masukkan URL website yang ingin dibersihkan
    2. Klik tombol "Ambil dan Bersihkan Konten"
    3. Preview hasil akan ditampilkan
    4. Klik "Download File TXT" untuk mengunduh hasil
    """)

if __name__ == "__main__":
    main()
