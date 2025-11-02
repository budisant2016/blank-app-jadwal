import streamlit as st
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
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cleaned_{domain}.txt"
                
                # Step 4: Simpan ke static folder
                file_path = save_to_static_folder(cleaned_content, filename)
                
                # Dapatkan base URL aplikasi
                try:
                    # Coba dapatkan URL base dari session state
                    if 'base_url' not in st.session_state:
                        # Untuk Streamlit Cloud, format URL-nya seperti:
                        # https://yourapp-name.streamlit.app/
                        script_name = os.environ.get('STREAMLIT_SCRIPT_NAME', '')
                        st.session_state.base_url = f"https://{st.secrets.get('URL', 'yourapp-name.streamlit.app')}"
                    
                    file_url = f"{st.session_state.base_url}/static/{filename}"
                    
                except:
                    # Fallback: berikan instruksi manual
                    file_url = f"/static/{filename}"
                
                st.session_state.cleaned_content = cleaned_content
                st.session_state.original_content = response.text
                st.session_state.file_url = file_url
                st.session_state.filename = filename
                st.session_state.local_path = str(file_path)
                
                st.success("✅ File berhasil disimpan sebagai static file!")
                
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {str(e)}")
    
    # Tampilkan hasil jika berhasil
    if 'file_url' in st.session_state:
        st.markdown("---")
        st.subheader("📁 Static File Hasil")
        
        # Tampilkan URL file
        st.success(f"**File berhasil disimpan:**")
        st.markdown(f"### 🔗 File: `{st.session_state.filename}`")
        
        # URL untuk mengakses file
        st.markdown("**URL untuk mengakses file:**")
        st.code(st.session_state.file_url, language="text")
        
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
