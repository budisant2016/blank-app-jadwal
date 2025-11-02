import streamlit as st
import ftplib
from io import StringIO
import requests
from bs4 import BeautifulSoup
import os
import shutil
from pathlib import Path

def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    elements_to_remove = [
        {'name': 'div', 'class': 'container persebaya-nav'},
        {'name': 'div', 'class': 'row mt-4 mb-2'},
        {'name': 'form', 'action': 'https://www.persebaya.id/search/result'},
        {'name': 'div', 'class': 'row mt-4 pl-md-5 pr-md-5'},
        {'name': 'div', 'id': 'footer-top'}
    ]
    
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

def save_to_static_folder(content, filename):
    """
    Menyimpan file ke folder static Streamlit
    """
    # Buat folder static jika belum ada
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    file_path = static_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

def upload_via_ftp(content, filename, ftp_config):
    """
    Upload file via FTP
    """
    try:
        # Connect to FTP server
        ftp = ftplib.FTP('ftpupload.net')
        ftp.login('if0_40314646', 'sm5z3gpN4cvaR')
        
        # Change to target directory
        ftp.cwd('htdocs')
        
        # Upload file
        file_obj = StringIO(content)
        ftp.storbinary(f'STOR {filename}', file_obj)
        ftp.quit()
        
        return True, f"ftp://{ftp_config['ftpupload.net']}/{ftp_config.get('htdocs', '')}/{filename}"
    
    except Exception as e:
        return False, str(e)

def main():
    st.set_page_config(
        page_title="HTML Content Cleaner - Static Hosting",
        page_icon="📁",
        layout="wide"
    )
    
    st.title("📁 HTML Content Cleaner - Static File Hosting")
    st.markdown("""
    Aplikasi ini akan:
    1. Membaca konten dari URL yang Anda masukkan
    2. Menghapus elemen-elemen HTML tertentu
    3. Menyimpan hasilnya sebagai file static di aplikasi ini
    4. Menyediakan URL untuk mengakses file
    """)
    
    # Input URL
    url = st.text_input(
        "Masukkan URL:",
        placeholder="https://example.com",
        value="https://www.persebaya.id"
    )
    
    if st.button("🔄 Proses dan Simpan sebagai Static File", type="primary"):
        if not url:
            st.error("⚠️ Silakan masukkan URL terlebih dahulu!")
            return
        
        try:
            with st.spinner("Sedang memproses dan menyimpan file..."):
                # Step 1: Ambil konten
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Step 2: Bersihkan konten
                cleaned_content = clean_html_content(response.text)
                
                # Step 3: Generate nama file unik
                domain = url.split('//')[-1].split('/')[0].replace('.', '_')
                import datetime
                #timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                xfilename = f"jadwal.txt"
                
                upload_via_ftp(cleaned_content, xfilename)
                
                # Step 4: Simpan ke static folder
                
                
                
                st.success("✅ File berhasil disimpan!")
                
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {str(e)}")
    
    
        # Instruksi penggunaan
        st.info("""
        **Cara mengakses file:**
        1. Copy URL di atas
        2. Buka tab browser baru
        3. Paste URL di address bar
        4. File akan terdownload otomatis
        """)
        
        # Tombol akses langsung
        st.markdown(f'<a href="{st.session_state.file_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">🌐 Buka File di Tab Baru</button></a>', unsafe_allow_html=True)
        
        # Preview konten
        with st.expander("📋 Preview Konten"):
            st.text_area(
                "Preview (pertama 1000 karakter):",
                st.session_state.cleaned_content[:1000] + "..." if len(st.session_state.cleaned_content) > 1000 else st.session_state.cleaned_content,
                height=200,
                key="preview"
            )
        
        # Statistik
        st.markdown("---")
        st.subheader("📊 Statistik")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Konten Asli", f"{len(st.session_state.original_content):,} char")
        with col2:
            st.metric("Hasil", f"{len(st.session_state.cleaned_content):,} char")
        with col3:
            reduction = len(st.session_state.original_content) - len(st.session_state.cleaned_content)
            reduction_percent = (reduction / len(st.session_state.original_content)) * 100
            st.metric("Pengurangan", f"{reduction:,} char", f"{reduction_percent:.1f}%")

if __name__ == "__main__":
    main()
