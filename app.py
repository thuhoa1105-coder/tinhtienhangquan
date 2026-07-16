import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Order Nhà Hàng Thu Hòa", layout="wide")

# --- KHỞI TẠO SESSION STATE (LƯU TRỮ DỮ LIỆU TẠM THỜI) ---
if 'order_dict' not in st.session_state:
    st.session_state.order_dict = {}
if 'order_history' not in st.session_state:
    st.session_state.order_history = []  # Lưu lịch sử các đơn hàng đã thanh toán

# --- THỰC ĐƠN ---
menu = {
    "Đồ ăn": {
        "Pizza Hải Sản": 150000, "ba chỉ nướng": 89000, "chân gà nướng": 80000, 
        "Mì Ý Bò Bằm": 95000, "Burger Gà": 65000, "Salad Trộn": 50000, 
        "Bít tết Bò Mỹ": 250000, "Sườn nướng BBQ": 180000, "combo nướng than hoa": 189000,
        "Cánh gà chiên mắm": 75000, "Lẩu cá diêu hồng": 200000, "Lẩu Thái hải sản": 300000
    },
    "Thức uống": {
        "Coca Cola": 20000, "Trà Đào Cam Sả": 35000, "Cà Phê Sữa": 25000,
        "Nước Suối": 10000, "Sinh tố Bơ": 45000, "Nước ép cam": 40000, "nước ép cà rốt": 45000,
        "Mojito chanh dây": 55000, "Bia Heineken": 30000
    }
}

# --- THANH SIDEBAR (ĐIỀU HƯỚNG & ĐĂNG NHẬP ADMIN) ---
st.sidebar.title("⚙️ Hệ thống Điều hướng")
role = st.sidebar.radio("Chọn vai trò:", ["Khách hàng (Order)", "Quản trị viên (Admin)"])

# ----------------------------------------------------
# 1. GIAO DIỆN KHÁCH HÀNG (ORDER CHÍNH)
# ----------------------------------------------------
if role == "Khách hàng (Order)":
    st.title("🍽️ Hệ thống Order Nhà Hàng THU HÒA")
    st.info("🎉 Ưu đãi: Giảm ngay 15% cho hoá đơn trên 1.000.000 VNĐ!")

    # Khu vực nhập thông tin Bàn và Ngày tháng
    st.subheader("📋 Thông tin bàn đặt")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        table_num = st.selectbox(
            "Chọn số bàn:", 
            [f"Bàn {i}" for i in range(1, 31)], 
            help="Chọn bàn khách đang ngồi"
        )
    with col_info2:
        order_date = st.date_input(
            "Ngày hóa đơn:", 
            datetime.date.today(),
            help="Mặc định là ngày hôm nay"
        )

    st.markdown("---")

    # Khu vực chọn món và Giỏ hàng
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("🛒 Chọn Món")
        category = st.selectbox("Chọn loại:", list(menu.keys()))
        item = st.selectbox("Chọn món:", list(menu[category].keys()))
        quantity = st.number_input("Số lượng:", min_value=1, step=1, value=1)
        
        if st.button("Thêm vào giỏ", use_container_width=True):
            price = menu[category][item]
            if item in st.session_state.order_dict:
                st.session_state.order_dict[item]["Số lượng"] += quantity
                st.session_state.order_dict[item]["Thành tiền"] = (
                    st.session_state.order_dict[item]["Số lượng"] * price
                )
            else:
                st.session_state.order_dict[item] = {
                    "Tên món": item,
                    "Đơn giá": price,
                    "Số lượng": quantity,
                    "Thành tiền": price * quantity
                }
            st.success(f"Đã cập nhật {item} vào giỏ!")

    with col2:
        st.subheader(f"🛍️ Giỏ hàng - {table_num} ({order_date.strftime('%d/%m/%Y')})")
        if st.session_state.order_dict:
            df = pd.DataFrame.from_dict(st.session_state.order_dict, orient='index')
            st.table(df[["Tên món", "Đơn giá", "Số lượng", "Thành tiền"]])
            
            tam_tinh = df["Thành tiền"].sum()
            giam_gia = (tam_tinh * 0.15) if tam_tinh > 1000000 else 0
            tong_thanh_toan = tam_tinh - giam_gia
            
            if giam_gia > 0:
                st.success(f"🎉 Bạn được giảm giá 15%!")
            
            st.write(f"**Tạm tính:** {tam_tinh:,.0f} VNĐ")
            if giam_gia > 0:
                st.write(f"**Giảm giá (15%):** -{giam_gia:,.0f} VNĐ")
            st.metric(label="Tổng thanh toán", value=f"{tong_thanh_toan:,.0f} VNĐ")
            
            # Nút chức năng thanh toán và xóa
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ Thanh toán & Xuất hóa đơn", type="primary", use_container_width=True):
                    # Tạo thông tin hóa đơn mới để lưu vào lịch sử Admin
                    chi_tiet_mon = ", ".join([f"{v['Tên món']} (x{v['Số lượng']})" for v in st.session_state.order_dict.values()])
                    
                    hoa_don = {
                        "Mã HĐ": f"HD{len(st.session_state.order_history) + 1:04d}",
                        "Ngày": order_date.strftime("%d/%m/%Y"),
                        "Bàn": table_num,
                        "Chi tiết món": chi_tiet_mon,
                        "Tổng tiền (VNĐ)": tong_thanh_toan
                    }
                    # Thêm vào bộ nhớ lịch sử
                    st.session_state.order_history.append(hoa_don)
                    
                    # Reset giỏ hàng hiện tại
                    st.session_state.order_dict = {}
                    st.balloons()
                    st.success("🎉 Đã thanh toán thành công! Hóa đơn đã được lưu vào hệ thống Admin.")
                    st.rerun()

            with col_btn2:
                if st.button("❌ Hủy/Xóa giỏ hàng", use_container_width=True):
                    st.session_state.order_dict = {}
                    st.toast("Đã xóa giỏ hàng hiện tại.")
                    st.rerun()
        else:
            st.info("Giỏ hàng đang trống. Vui lòng chọn món ăn ở cột bên trái.")

# ----------------------------------------------------
# 2. GIAO DIỆN QUẢN TRỊ VIÊN (ADMIN PANEL)
# ----------------------------------------------------
elif role == "Quản trị viên (Admin)":
    st.title("🔑 Trang Quản Lý Admin")
    
    # Thiết lập mật khẩu bảo mật đơn giản
    password = st.text_input("Nhập mật khẩu Admin:", type="password")
    
    if password == "2005":  # Mật khẩu mặc định là: admin123
        st.success("Đăng nhập thành công với quyền Admin!")
        st.markdown("---")
        
        st.subheader("📊 Thống kê doanh thu & Đơn hàng")
        
        if st.session_state.order_history:
            # Chuyển đổi lịch sử đơn hàng thành DataFrame để xử lý
            df_history = pd.DataFrame(st.session_state.order_history)
            
            # Khối hiển thị chỉ số nhanh (KPIs)
            total_orders = len(df_history)
            total_revenue = df_history["Tổng tiền (VNĐ)"].sum()
            
            col_kpi1, col_kpi2 = st.columns(2)
            with col_kpi1:
                st.metric(label="Tổng số đơn đã thanh toán", value=total_orders)
            with col_kpi2:
                st.metric(label="Tổng doanh thu thực tế", value=f"{total_revenue:,.0f} VNĐ")
            
            st.markdown("---")
            st.subheader("📝 Danh sách hóa đơn chi tiết")
            st.dataframe(df_history, use_container_width=True)
            
            # Nút xóa dữ liệu lịch sử để test lại từ đầu
            if st.button("🗑️ Xóa toàn bộ lịch sử đơn hàng"):
                st.session_state.order_history = []
                st.warning("Đã xóa toàn bộ lịch sử hóa đơn.")
                st.rerun()
        else:
            st.info("Chưa có đơn hàng nào được thanh toán trong phiên làm việc này.")
            
    elif password != "":
        st.error("Mật khẩu không đúng! Vui lòng thử lại.")
