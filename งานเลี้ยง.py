import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
import base64
import os
import random

# --- 1. ใส่ API ---
SHEETDB_URL = "https://sheetdb.io/api/v1/6141z8nhjv07m" 
IMGBB_API_KEY = "104f3d1f3d07a02f98c90c3ac0f60d9d"

# --- 2. การตั้งค่าพื้นฐาน ---
CLASS_NAME = "CT46"
TARGET_AMOUNT_PER_PERSON = 419
TOTAL_PEOPLE_TARGET = 75
TOTAL_MONEY_TARGET = 26000
COMMENTS_FILE = "comments_data.csv"

EXPENSE_DETAILS = {
    "ค่าอาหาร": 55,
    "ค่าเครื่องดื่ม": 27,
    "ค่าสถานที่และเบ็ดเตล็ด": 18
}

st.set_page_config(page_title=f"เก็บเงินเลี้ยงรุ่น {CLASS_NAME}", page_icon="🥂", layout="wide")

# ==========================================
# ฟังก์ชันระบบฐานข้อมูล (เพิ่มตัวจับ Error ละเอียด)
# ==========================================
def load_data():
    try:
        response = requests.get(SHEETDB_URL)
        if response.status_code == 200:
            data = response.json()
            if data and "error" not in data:
                df = pd.DataFrame(data)
                df['จำนวนเงิน'] = pd.to_numeric(df['จำนวนเงิน'], errors='coerce').fillna(0)
                return df
    except Exception as e:
        pass # ปิดแจ้งเตือนตอนโหลดหน้าแรกไปก่อน
    return pd.DataFrame(columns=["วันที่แจ้ง", "ชื่อ", "จำนวนเงิน", "วันที่โอน", "ลิงก์สลิป", "หมายเหตุ"])

def upload_image(image_file):
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": base64.b64encode(image_file.getvalue()).decode("utf-8")
    }
    try:
        res = requests.post(url, data=payload)
        if res.status_code == 200:
            return res.json()['data']['url']
        else:
            st.error(f"❌ ImgBB Error: รหัส {res.status_code} - {res.text}")
            return None
    except Exception as e:
        st.error(f"❌ ไม่สามารถเชื่อมต่อระบบอัปโหลดรูปได้: {e}")
        return None

def load_comments():
    if os.path.exists(COMMENTS_FILE):
        return pd.read_csv(COMMENTS_FILE)
    else:
        return pd.DataFrame(columns=["วันที่", "ข้อความ"])

def render_floating_comments():
    df_comments = load_comments()
    if df_comments.empty:
        return
    recent_comments = df_comments.tail(15)["ข้อความ"].tolist()
    css_animation = """
    <style>
    .floating-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999; overflow: hidden; }
    .floating-text { position: absolute; white-space: nowrap; font-size: 28px; font-weight: bold; color: #FFD700; text-shadow: 2px 2px 4px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; opacity: 0.9; }
    @keyframes floatLeft { from { transform: translateX(100vw); } to { transform: translateX(-100%); } }
    </style>
    """
    html_comments = '<div class="floating-container">'
    for i, text in enumerate(recent_comments):
        top_pos = random.randint(10, 80)
        duration = random.randint(10, 20)
        delay = random.randint(0, 10)
        style = f"top: {top_pos}%; animation: floatLeft {duration}s linear {delay}s infinite;"
        html_comments += f'<div class="floating-text" style="{style}">{text}</div>'
    html_comments += '</div>'
    st.markdown(css_animation + html_comments, unsafe_allow_html=True)

df_display = load_data()
current_people = len(df_display)
current_money = df_display["จำนวนเงิน"].sum() if not df_display.empty else 0

render_floating_comments()

st.title(f"🥂 ระบบลงทะเบียนงานเลี้ยงรุ่น {CLASS_NAME}")
st.write(f"ยอดเงินที่ต้องชำระ: **{TARGET_AMOUNT_PER_PERSON} บาทต่อท่าน**")

st.markdown("### 📈 ความคืบหน้าของรุ่นเรา")
col_prog1, col_prog2 = st.columns(2)
with col_prog1:
    st.write(f"**👥 จำนวนคนโอนแล้ว: {current_people} / {TOTAL_PEOPLE_TARGET} คน**")
    st.progress(min(current_people / TOTAL_PEOPLE_TARGET, 1.0) if TOTAL_PEOPLE_TARGET > 0 else 0)
with col_prog2:
    st.write(f"**💰 ยอดรวมตอนนี้: {current_money:,.2f} / {TOTAL_MONEY_TARGET:,.2f} บาท**")
    st.progress(min(current_money / TOTAL_MONEY_TARGET, 1.0) if TOTAL_MONEY_TARGET > 0 else 0)

st.divider()

tab_reg, tab_dash, tab_comment = st.tabs(["📝 แจ้งโอนเงิน", "📊 แดชบอร์ดสรุปยอด", "💬 กระดานแสดงความคิดเห็น"])

with tab_reg:
    col_form, col_bank = st.columns([2, 1])
    with col_bank:
        st.subheader("🏦 ช่องทางชำระเงิน")
        st.info(f"**ธนาคาร:** กสิกรไทย\n\n**เลขบัญชี:** xxx-x-xxxxx-x\n\n**ชื่อบัญชี:** นาย... (CT46)")

    with col_form:
        st.subheader("➕ แจ้งโอนเงินที่นี่")
        with st.form("payment_form", clear_on_submit=True):
            name = st.text_input("ชื่อ-นามสกุล (หรือฉายา)")
            amount = st.number_input("จำนวนเงินที่โอน (บาท)", min_value=0.0, value=float(TARGET_AMOUNT_PER_PERSON))
            date = st.date_input("วันที่โอน", datetime.now())
            uploaded_slip = st.file_uploader("แนบหลักฐานการโอนเงิน (JPG, PNG)", type=['png', 'jpg', 'jpeg'])
            note = st.text_area("หมายเหตุ (ถ้ามี)")
            submit_button = st.form_submit_button("ส่งข้อมูลชำระเงิน")

            if submit_button:
                if name and uploaded_slip:
                    with st.spinner('กำลังบันทึกข้อมูลและอัปโหลดสลิป...'):
                        slip_url = upload_image(uploaded_slip)
                        if slip_url:
                            submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            payload = {
                                "data": {
                                    "วันที่แจ้ง": submission_date,
                                    "ชื่อ": name,
                                    "จำนวนเงิน": amount,
                                    "วันที่โอน": str(date),
                                    "ลิงก์สลิป": slip_url,
                                    "หมายเหตุ": note
                                }
                            }
                            try:
                                res = requests.post(SHEETDB_URL, json=payload)
                                if res.status_code == 201:
                                    st.success(f"บันทึกข้อมูลสำเร็จ! ข้อมูลถูกส่งเข้าระบบแล้ว 🎉")
                                    st.info("กรุณารีเฟรชหน้าเว็บเพื่อดูยอดรวมอัปเดต")
                                else:
                                    st.error(f"❌ บันทึกข้อมูลไม่สำเร็จ SheetDB Error: รหัส {res.status_code} - {res.text}")
                            except Exception as e:
                                st.error(f"❌ ไม่สามารถเชื่อมต่อระบบฐานข้อมูลได้: {e}")
                else:
                    st.error("กรุณากรอกชื่อ และแนบสลิปด้วยครับ")

with tab_dash:
    if not df_display.empty:
        st.subheader("📊 การจัดสรรงบประมาณค่าใช้จ่าย")
        col_chart, col_details = st.columns([1.5, 1])
        expense_data = [{"Category": k, "Percentage": v, "Amount": (v / 100) * current_money} for k, v in EXPENSE_DETAILS.items()]
        df_expense = pd.DataFrame(expense_data)
        with col_chart:
            fig = px.pie(df_expense, values='Percentage', names='Category', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        with col_details:
            st.write("**งบประมาณที่จัดสรรได้ตอนนี้:**")
            for _, row in df_expense.iterrows():
                st.info(f"👉 **{row['Category']}** ({row['Percentage']}%): **{row['Amount']:,.2f}** บาท")
        st.divider()
        st.subheader("📋 รายชื่อผู้ที่ชำระเงินแล้ว")
        st.data_editor(df_display, column_config={"ลิงก์สลิป": st.column_config.LinkColumn("คลิกดูสลิป")}, hide_index=True, use_container_width=True)
    else:
        st.warning("ยังไม่มีข้อมูลการชำระเงิน")

with tab_comment:
    st.subheader("💬 ปล่อยกระสุนข้อความ (Anonymous)")
    with st.form("comment_form", clear_on_submit=True):
        new_comment = st.text_input("พิมพ์ข้อความของคุณที่นี่ (สั้นๆ จะสวยกว่า):")
        submit_comment = st.form_submit_button("ส่งข้อความลอยหน้าจอ 🚀")
        if submit_comment:
            if new_comment.strip():
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                comment_data = pd.DataFrame([[now_str, new_comment.strip()]], columns=["วันที่", "ข้อความ"])
                df_comments = load_comments()
                df_comments = pd.concat([df_comments, comment_data], ignore_index=True)
                df_comments.to_csv(COMMENTS_FILE, index=False, encoding='utf-8-sig')
                st.success("ส่งข้อความสำเร็จ! รีเฟรชหน้าเว็บ 1 รอบเพื่อดูข้อความลอยได้เลยครับ")
            else:
                st.error("กรุณาพิมพ์ข้อความก่อนกดส่งครับ")
