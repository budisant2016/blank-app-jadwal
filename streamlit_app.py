import streamlit as st
import requests
from bs4 import BeautifulSoup
import ftplib
from io import BytesIO
import datetime


def clean_html_content(html_content):
    """
    Membersihkan HTML dengan menghapus elemen-elemen tertentu
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Daftar elemen yang akan dihapus
    elements_to_remove = [
            {'name': 'div', 'class': 'container persebaya-nav'},
            {'name': 'h4', 'class': 'modal-title', 'text': 'Search'},
            {'name': 'button', 'class': 'close', 'attrs': {'data-dismiss': 'modal'}},
            {'name': 'div', 'class': 'row mt-4 mb-2'},
            {'name': 'div', 'class': 'col-md-12 px-0 px-md-3'},
            {'name': 'div', 'class': 'col-12 col-md-3 order-last order-md-last text-center'},
            {'name': 'form', 'attrs': {'action': 'https://www.persebaya.id/search/result', 'class': 'form-inline navbar-right ml-auto', 'method': 'GET', 'role': 'search'}},
            {'name': 'div', 'id': 'footer-top', 'class': 'row align-items-center text-center pb-5 pb-md-3 pt-md-4'}
        ]
    
    # Menghapus setiap elemen yang ditentukan
    for element_config in elements_to_remove:
            if 'class' in element_config and 'text' in element_config:
                elements = soup.find_all(element_config['name'], 
                                       class_=element_config['class'],
                                       string=element_config['text'])
            elif 'class' in element_config:
                elements = soup.find_all(element_config['name'], class_=element_config['class'])
            elif 'attrs' in element_config:
                elements = soup.find_all(element_config['name'], attrs=element_config['attrs'])
            else:
                elements = soup.find_all(element_config['name'])
            
            for element in elements:
                element.decompose()
    
    return str(soup)

def upload_via_ftp(content, filename, ftp_config):
    """
    Upload file via FTP ke hosting
    """
    try:
        # Connect to FTP server
        ftp = ftplib.FTP(ftp_config['host'])
        ftp.login(ftp_config['user'], ftp_config['pass'])
        
        # Change to target directory
        if 'path' in ftp_config:
            ftp.cwd(ftp_config['path'])
        
        # Upload file sebagai binary
        content_bytes = content.encode('utf-8')
        file_obj = BytesIO(content_bytes)
        
        # Gunakan STORBINARY untuk upload file
        ftp.storbinary(f'STOR {filename}', file_obj)
        
        # Close connection
        ftp.quit()
        
        return True, "File berhasil diupload ke hosting"
    
    except Exception as e:
        return False, f"Error FTP: {str(e)}"

def main():
    st.set_page_config(
        page_title="Persebaya Jadwal Auto Upload",
        page_icon="⚽",
        layout="centered"
    )
    
    st.title("⚽ Persebaya Jadwal Auto Upload")
    st.info("Aplikasi sedang berjalan...")
    
    # Konfigurasi FTP (hardcoded sesuai permintaan)
    FTP_CONFIG = {
        'host': "157.66.54.106",
        'user': "appbonek",
        'pass': "jikasupport081174",
        'path': "/"
    }
    
    # URL target (hardcoded sesuai permintaan)
    TARGET_URL = "https://www.persebaya.id/jadwal-pertandingan/91/persebaya-surabaya"
    FILENAME = "jadwal.txt"
    
    # Progress bar dan status
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Ambil konten dari URL
        status_text.text("📥 Mengambil data dari Persebaya...")
        progress_bar.progress(25)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Step 2: Bersihkan konten HTML
        status_text.text("🧹 Membersihkan konten HTML...")
        progress_bar.progress(50)
        
        cleaned_content = clean_html_content(response.text)
        
        # Tambahkan timestamp
        timestamp = datetime.datetime.now().strftime("<!-- Generated at: %Y-%m-%d %H:%M:%S -->\n")
        final_content = timestamp + cleaned_content
        
        # Step 3: Upload ke hosting via FTP
        status_text.text("📤 Mengupload ke hosting...")
        progress_bar.progress(75)
        
        success, message = upload_via_ftp(final_content, FILENAME, FTP_CONFIG)
        
        if success:
            status_text.text("✅ Proses selesai!")
            progress_bar.progress(100)
            
            st.success(f"""
            ✅ **File berhasil diupload!**
            
            **Detail:**
            - File: `{FILENAME}`
            - Host: `{FTP_CONFIG['host']}`
            - Path: `{FTP_CONFIG['path']}`
            - URL: `https://if0_40314646.ifastnet.com/{FILENAME}`
            - Waktu: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """)
            
            # Tampilkan preview
            with st.expander("📋 Preview Konten (1000 karakter pertama)"):
                st.text_area(
                    "Konten yang diupload:",
                    final_content[:1000] + "..." if len(final_content) > 1000 else final_content,
                    height=300,
                    key="preview"
                )
            
            # Statistik
            st.subheader("📊 Statistik")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Konten Asli", f"{len(response.text):,} char")
            with col2:
                st.metric("Setelah Dibersihkan", f"{len(final_content):,} char")
            with col3:
                reduction = len(response.text) - len(final_content)
                reduction_percent = (reduction / len(response.text)) * 100
                st.metric("Pengurangan", f"{reduction:,} char", f"{reduction_percent:.1f}%")
                
        else:
            st.error(f"❌ {message}")
            progress_bar.progress(0)
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Gagal mengambil data dari Persebaya: {str(e)}")
        progress_bar.progress(0)
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {str(e)}")
        progress_bar.progress(0)
    
    # Informasi konfigurasi
    with st.expander("🔧 Konfigurasi Saat Ini"):
        st.code(f"""
        URL Target: {TARGET_URL}
        FTP Host: {FTP_CONFIG['host']}
        FTP User: {FTP_CONFIG['user']}
        FTP Path: {FTP_CONFIG['path']}
        Output File: {FILENAME}
        """)
    
    # Informasi tambahan
    st.markdown("---")
    st.markdown("""
    ### 📝 Informasi:
    - Data diambil dari: [Persebaya Jadwal](https://www.persebaya.id/jadwal-pertandingan/91/persebaya-surabaya)
    - File disimpan di: `htdocs/jadwal.txt` pada hosting
    - File dapat diakses via: `https://if0_40314646.ifastnet.com/jadwal.txt`
    - Proses membersihkan 5 elemen HTML tertentu
    - **Script berjalan otomatis setiap kali halaman ini diakses**
    """)

    st.title("Streamlit Keep-Alive Demo 🚀")

    st.write("Aplikasi ini menampilkan waktu saat ini dan bisa dipakai untuk uji anti-sleep.")
    
    st.write("Waktu sekarang:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Opsional: tampilan log keepalive
    try:
        with open("../keepalive.log") as f:
            log = f.readlines()[-5:]  # 5 log terakhir
        st.write("Log keepalive terakhir:")
        st.write("".join(log))
    except:
        st.write("Belum ada log keepalive.")

if __name__ == "__main__":
    main()
