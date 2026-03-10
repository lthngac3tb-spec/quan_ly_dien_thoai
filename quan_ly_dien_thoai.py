import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# --- CẤU HÌNH ---
FILE_LOP = "danh_sach_lop.xlsx"
mui_gio_vn = pytz.timezone('Asia/Ho_Chi_Minh')

st.set_page_config(page_title="Quản lý Điện thoại", page_icon="📱")
st.title("📱 QUẢN LÝ ĐIỆN THOẠI")

# Đọc dữ liệu
# --- ĐOẠN CODE "LỌC" DỮ LIỆU CỰC MẠNH ---
if os.path.exists(FILE_LOP):
    df = pd.read_excel(FILE_LOP)
    
    # Ép tất cả STT về dạng chuỗi 2 chữ số (VD: 1 -> "01", 01 -> "01")
    # Điều này giúp sửa lỗi khi Excel tự ý đổi 01 thành 1
    df['STT'] = df['STT'].astype(str).apply(lambda x: x.split('.')[0].zfill(2))
    
    # Ép các cột khác về dạng chuỗi để tránh lỗi TypeError lúc nãy
    for col in ['TrangThai', 'GioCat', 'GioTra']:
        df[col] = df[col].astype(str).replace('nan', '')

tab1, tab2 = st.tabs(["📸 Trạm Quét", "📊 Danh sách"])

with tab1:
    che_do = st.radio("Chế độ:", ["Thu máy (Cất)", "Trả máy (Lấy về)"], horizontal=True)
    
    # Ô nhập liệu thông minh
    ma_quet = st.text_input("Chạm vào đây -> Chọn biểu tượng Camera trên bàn phím để quét mã QR:", key="qr_input")
    
    if ma_quet:
        stt_nhan = ma_quet.strip().zfill(2)
        if stt_nhan in df['STT'].values:
            idx = df.index[df['STT'] == stt_nhan][0]
            ten = df.at[idx, 'HoTen']
            now = datetime.now(mui_gio_vn).strftime("%H:%M %d/%m")

            if che_do == "Thu máy (Cất)":
                df.at[idx, 'TrangThai'] = "✅ Đã cất"
                df.at[idx, 'GioCat'] = now
                st.success(f"Đã thu máy của: {ten}")
            else:
                df.at[idx, 'TrangThai'] = "🏠 Đã trả"
                df.at[idx, 'GioTra'] = now
                st.info(f"Đã trả máy cho: {ten}")
            
            df.to_excel(FILE_LOP, index=False)
            st.balloons()
        else:
            st.warning(f"Không tìm thấy học sinh có số STT: {stt_nhan}")

with tab2:
    st.subheader("Tình trạng lớp")
    st.dataframe(df, use_container_width=True)
    if st.button("Làm mới ngày mới"):
        df['TrangThai'] = "Chưa cất"
        df['GioCat'] = ""
        df['GioTra'] = ""
        df.to_excel(FILE_LOP, index=False)
        st.rerun()

