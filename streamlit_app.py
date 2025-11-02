import streamlit as st
import requests
from bs4 import BeautifulSoup
import ftplib
from io import StringIO

def upload_via_ftp(content, filename):
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
        st.markdown(content)
        ftp.storbinary(f'STOR {filename}', file_obj)
        ftp.quit()
        
        return True, f"ftp://{ftp_config['ftpupload.net']}/{ftp_config.get('htdocs', '')}/{filename}"
    
    except Exception as e:
        return False, str(e)



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
    3. Menampilkan hasilnya langsung di halaman ini
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
    
    # Tampilkan hasil jika sudah ada
    if 'cleaned_content' in st.session_state:
        st.markdown("---")
        st.subheader("📋 Hasil Konten yang Sudah Dibersihkan")
        
        # Tampilkan konten lengkap dalam text area yang dapat di-scroll
        #st.text_area(
        #    "Konten HTML yang sudah dibersihkan:",
        #    st.session_state.cleaned_content,
        #    height=600,
        #    key="cleaned_content_display"
        #)
        upload_via_ftp(st.session_state.cleaned_content, 'testing.txt')
        
        # Tampilkan statistik
        st.markdown("---")
        st.subheader("📊 Statistik")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Konten Asli", 
                f"{len(st.session_state.original_content):,} karakter"
            )
        with col2:
            st.metric(
                "Setelah Dibersihkan", 
                f"{len(st.session_state.cleaned_content):,} karakter"
            )
        with col3:
            reduction = len(st.session_state.original_content) - len(st.session_state.cleaned_content)
            reduction_percent = (reduction / len(st.session_state.original_content)) * 100
            st.metric(
                "Pengurangan", 
                f"{reduction:,} karakter",
                f"{reduction_percent:.1f}%"
            )

    # Informasi tambahan
    st.markdown("---")
    st.markdown("""
    ### 📝 Cara Menggunakan:
    1. Masukkan URL website yang ingin dibersihkan (contoh: https://www.persebaya.id)
    2. Klik tombol "Ambil dan Bersihkan Konten"
    3. Hasil akan langsung ditampilkan di text area di bawah
    4. Anda dapat menyalin konten langsung dari text area tersebut
    """)

if __name__ == "__main__":
    main()




