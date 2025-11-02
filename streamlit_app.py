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

def upload_via_ftp(content, filename, ftp_config):
    """
    Upload file via FTP ke hosting
    """
    try:
        # Connect to FTP server
        st.info("🔄 Menghubungkan ke FTP server...")
        ftp = ftplib.FTP(ftp_config['host'])
        ftp.login(ftp_config['user'], ftp_config['pass'])
        
        # Change to target directory
        if 'path' in ftp_config:
            st.info(f"📁 Pindah ke directory: {ftp_config['path']}")
            ftp.cwd(ftp_config['path'])
        
        # Upload file sebagai binary
        st.info(f"📤 Mengupload file: {filename}")
        
        # Convert string to bytes dengan encoding UTF-8
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
    st.markdown("""
    Aplikasi ini akan secara otomatis:
    1. Mengambil jadwal pertandingan dari [Persebaya](https://www.persebaya.id/jadwal-pertandingan/91/persebaya-surabaya)
    2. Membersihkan elemen HTML yang tidak diperlukan
    3. Mengupload hasilnya ke hosting sebagai `jadwal.txt`
    """)
    
    # Konfigurasi FTP (hardcoded sesuai permintaan)
    FTP_CONFIG = {
        'host': "ftpupload.net",
        'user': "if0_40314646",
        'pass': "sm5z3gpN4cvaR",
        'path': "htdocs"
    }
    
    # URL target (hardcoded sesuai permintaan)
    TARGET_URL = "https://www.persebaya.id/jadwal-pertandingan/91/persebaya-surabaya"
    FILENAME = "jadwal.txt"
    
    if st.button("🚀 Jalankan Proses Auto Upload", type="primary"):
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
                
                st.success("""
                ✅ **File berhasil diupload!**
                
                **Detail:**
                - File: `jadwal.txt`
                - Host: `ftpupload.net`
                - Path: `htdocs`
                - URL: `https://if0_40314646.ifastnet.com/jadwal.txt`
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
    """)

if __name__ == "__main__":
    main()
