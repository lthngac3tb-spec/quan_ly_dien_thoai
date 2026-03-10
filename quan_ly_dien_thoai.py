import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os
import io

# --- 1. CẤU HÌNH HỆ THỐNG ---
FILE_LOP = "danh_sach_lop.xlsx"
mui_gio_vn = pytz.timezone('Asia/Ho_Chi_Minh')

st.set_page_config(page_title="Quản lý Điện thoại", page_icon="📱", layout="centered")
st.title("📱 HỆ THỐNG QUẢN LÝ ĐIỆN THOẠI")

# --- 2. HÀM ĐỌC VÀ LÀM SẠCH DỮ LIỆU ---
def load_data():
    if os.path.exists(FILE_LOP):
        df = pd.read_excel(FILE_LOP)
        # Ép STT về dạng chuỗi "01", "02"...
        df['STT'] = df['STT'].astype(str).apply(lambda x: x.split('.')[0].strip().zfill(2))
        # Ép các cột khác về dạng chuỗi để không lỗi TypeError
        for col in ['HoTen', 'TrangThai', 'GioCat', 'GioTra']:
            if col in df.columns:
                df[col] = df[col].astype(str).replace('nan', '')
        return df
    else:
        st.error(f"Không tìm thấy file {FILE_LOP} trên GitHub!")
        return None

df = load_data()

if df is not None:
    tab1, tab2 = st.tabs(["📸 Trạm Quét", "📊 Danh sách & Báo cáo"])

    # --- TAB 1: XỬ LÝ THU / TRẢ MÁY ---
    with tab1:
        st.subheader("📸 Thu hoặc Trả máy")
        che_do = st.radio("Chế độ:", ["Thu máy (Cất)", "Trả máy (Lấy về)"], horizontal=True)
        
        # Nhập mã số
        ma_quet = st.text_input("Nhập STT (Ví dụ: 01, 05) hoặc dùng camera bàn phím:", key="qr_input")
        
        if ma_quet:
            stt_nhan = ma_quet.strip().zfill(2)
            if stt_nhan in df['STT'].values:
                idx = df.index[df['STT'] == stt_nhan][0]
                ten = df.at[idx, 'HoTen']
                bay_gio = datetime.now(mui_gio_vn).strftime("%H:%M %d/%m")

                if che_do == "Thu máy (Cất)":
                    df.at[idx, 'TrangThai'] = "✅ Đã cất"
                    df.at[idx, 'GioCat'] = bay_gio
                    st.success(f"Đã thu máy của: {ten}")
                else:
                    df.at[idx, 'TrangThai'] = "🏠 Đã trả"
                    df.at[idx, 'GioTra'] = bay_gio
                    st.info(f"Đã trả máy cho: {ten}")
                
                # Lưu lại file Excel
                df.to_excel(FILE_LOP, index=False)
                st.balloons()
            else:
                st.warning(f"Không tìm thấy học sinh số: {stt_nhan}")

    # --- TAB 2: DANH SÁCH & XUẤT FILE ---
    with tab2:
        # Thống kê nhanh ở trên đầu
        col1, col2 = st.columns(2)
        tong_so = len(df)
        da_cat = len(df[df['TrangThai'] == "✅ Đã cất"])
        col1.metric("Tổng sĩ số", f"{tong_so} HS")
        col2.metric("Đã cất máy", f"{da_cat} máy")

        st.divider()
        st.subheader("Bảng chi tiết tình trạng")
        st.dataframe(df, use_container_width=True)

        # PHẦN XUẤT FILE EXCEL
        st.write("---")
        try:
            ngay_hien_tai = datetime.now(mui_gio_vn).strftime("%d_%m_%Y")
            buffer = io.BytesIO()
            # Dùng ExcelWriter với sheet_name cụ thể để tránh lỗi IndexError
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='BaoCaoNgay')
            
            st.download_button(
                label=f"💾 Tải file Excel ngày {ngay_hien_tai}",
                data=buffer.getvalue(),
                file_name=f"Bao_Cao_Lop_{ngay_hien_tai}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Lỗi tạo file tải về: {e}")

        # NÚT RESET NGÀY MỚI
        st.write("---")
        if st.button("🔄 Reset dữ liệu sang ngày mới"):
            df['TrangThai'] = "Chưa cất"
            df['GioCat'] = ""
            df['GioTra'] = ""
            df.to_excel(FILE_LOP, index=False)
            st.warning("Đã reset dữ liệu. Hãy F5 lại app.")
            st.rerun()
