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
   # --- TAB 1: XỬ LÝ THU / TRẢ MÁY ---
    with tab1:
        st.subheader("📸 Thu hoặc Trả máy")
        che_do = st.radio("Chế độ:", ["Thu máy (Cất)", "Trả máy (Lấy về)"], horizontal=True)
        
        # SỬA Ở ĐÂY: Dùng form để tự động xóa dữ liệu sau khi nhấn Enter
        with st.form(key='form_quet_ma', clear_on_submit=True):
            ma_quet = st.text_input("Nhập STT (Ví dụ: 01, 05) rồi nhấn Enter:")
            submit_button = st.form_submit_button(label='Xác nhận')
        
        # Xử lý dữ liệu khi người dùng nhấn Enter (Submit form)
        if submit_button and ma_quet:
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
   # --- PHẦN XUẤT FILE EXCEL "SIÊU LỲ" - KHÔNG THỂ LỖI ---
        st.write("---")
        try:
            from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
            from openpyxl.utils import get_column_letter
            from openpyxl import Workbook

            ngay_hien_tai = datetime.now(mui_gio_vn).strftime("%d_%m_%Y")
            buffer = io.BytesIO()
            
            wb = Workbook()
            ws = wb.active
            ws.title = "BaoCao"

            # 1. Ghi tiêu đề và dữ liệu (Ép tất cả về String để chống lỗi len)
            headers = list(df.columns)
            ws.append(headers)
            for r in df.values.tolist():
                # Chuyển mọi giá trị thành chuỗi, ô trống thành ""
                row_data = [str(x) if str(x) != 'nan' else "" for x in r]
                ws.append(row_data)

            # 2. Định dạng Header
            blue_fill = PatternFill(start_color="B8CCE4", end_color="B8CCE4", fill_type="solid")
            bold_font = Font(bold=True)
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                                top=Side(style='thin'), bottom=Side(style='thin'))

            for col_num in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col_num)
                cell.fill = blue_fill
                cell.font = bold_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border

            # 3. Định dạng hàng dữ liệu & Ép độ rộng cột
            # Cột 1: STT, Cột 2: Họ Tên, Cột 3: Trạng thái, Cột 4: Giờ cất, Cột 5: Giờ trả
            column_widths = [10, 25, 15, 15, 15] # Độ rộng cố định cho từng cột
            
            for i, width in enumerate(column_widths):
                ws.column_dimensions[get_column_letter(i + 1)].width = width

            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                for cell in row:
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    # Riêng cột Họ Tên (cột 2) thì căn trái cho dễ đọc
                    if cell.column == 2:
                        cell.alignment = Alignment(horizontal='left', vertical='center')

            # 4. Lưu workbook
            wb.save(buffer)
            
            st.download_button(
                label=f"💾 Tải báo cáo Excel (Bản chuẩn {ngay_hien_tai})",
                data=buffer.getvalue(),
                file_name=f"Bao_Cao_Lop_{ngay_hien_tai}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}. Hãy báo lại để thầy sửa ngay!")

        # NÚT RESET NGÀY MỚI
        st.write("---")
        if st.button("🔄 Reset dữ liệu sang ngày mới"):
            df['TrangThai'] = "Chưa cất"
            df['GioCat'] = ""
            df['GioTra'] = ""
            df.to_excel(FILE_LOP, index=False)
            st.warning("Đã reset dữ liệu. Hãy F5 lại app.")
            st.rerun()






