import streamlit as st
import pandas as pd
from datetime import datetime
import os
import os
os.system("pip install openpyxl")

# --- CẤU HÌNH BAN ĐẦU ---
FILE_LOP = "danh_sach_lop.xlsx"

# Tạo file mẫu nếu chưa có
if not os.path.exists(FILE_LOP):
    df_mau = pd.DataFrame({
        "STT": ["01", "02", "03"],
        "HoTen": ["Nguyễn Văn A", "Trần Thị B", "Lê Văn C"],
        "TrangThai": ["Chưa cất", "Chưa cất", "Chưa cất"],
        "GioCat": ["", "", ""],
        "GioTra": ["", "", ""]
    })
    df_mau.to_excel(FILE_LOP, index=False)

st.title("📱 QUẢN LÝ ĐIỆN THOẠI LỚP")

# --- GIAO DIỆN CHÍNH ---
tab1, tab2 = st.tabs(["📸 Quét Mã QR", "📊 Danh sách Lớp"])

with tab1:
    st.subheader("Trạm Thu/Trả Máy")
    che_do = st.radio("Chọn chế độ:", ["Thu máy (Cất)", "Trả máy (Lấy về)"], horizontal=True)
    
    # Ở đây chúng ta sẽ dùng một ô nhập text giả lập máy quét 
    # (Vì hầu hết máy quét QR cầm tay hoặc Camera đều trả về text)
    ma_quet = st.text_input("Đưa camera vào mã QR (hoặc nhập STT):")
    
    if ma_quet:
        df = pd.read_excel(FILE_LOP)
        # Chuyển STT về dạng string để so sánh cho chuẩn
        df['STT'] = df['STT'].astype(str).str.zfill(2) 
        ma_quet = ma_quet.zfill(2)

        if ma_quet in df['STT'].values:
            idx = df.index[df['STT'] == ma_quet][0]
            ten_hs = df.at[idx, 'HoTen']
            now = datetime.now().strftime("%H:%M %d/%m")

            # CHỖ SỬA QUAN TRỌNG: Ép kiểu dữ liệu cột thành Object (Chuỗi) trước khi gán
            df['TrangThai'] = df['TrangThai'].astype(str)
            df['GioCat'] = df['GioCat'].astype(str)
            df['GioTra'] = df['GioTra'].astype(str)

            if che_do == "Thu máy (Cất)":
                df.at[idx, 'TrangThai'] = "✅ Đã cất"
                df.at[idx, 'GioCat'] = now
                st.success(f"Đã thu máy của: {ten_hs}")
            else:
                df.at[idx, 'TrangThai'] = "🏠 Đã trả"
                df.at[idx, 'GioTra'] = now
                st.info(f"Đã trả máy cho: {ten_hs}")
            
            # Xóa các giá trị 'nan' (trống) trông cho đẹp
            df = df.replace('nan', '')
            df.to_excel(FILE_LOP, index=False)
        else:
            st.error("Không tìm thấy học sinh này!")

with tab2:
    st.subheader("Tình trạng hiện tại")
    df_hien_thi = pd.read_excel(FILE_LOP)
    st.dataframe(df_hien_thi, use_container_width=True)
    
    # Nút reset ngày mới
    if st.button("Reset ngày mới"):
        df_hien_thi['TrangThai'] = "Chưa cất"
        df_hien_thi['GioCat'] = ""
        df_hien_thi['GioTra'] = ""
        df_hien_thi.to_excel(FILE_LOP, index=False)
        st.rerun()




