import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page Config
st.set_page_config(page_title="GIEPL ERP Pro", layout="wide")

# Database Setup
conn = sqlite3.connect('giepl_data.db', check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS employees 
                (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, address TEXT, bank_name TEXT, acc_no TEXT, ifsc TEXT)''')
conn.execute('''CREATE TABLE IF NOT EXISTS equipment 
                (id INTEGER PRIMARY KEY, name TEXT, model TEXT, reg_no TEXT, exp_date DATE)''')
conn.commit()

# Login System
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 GIEPL ERP Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Galat username ya password!")
    st.stop()

# Sidebar
st.sidebar.title("🏗️ GIEPL ERP")
choice = st.sidebar.selectbox("मेनू", ["डैशबोर्ड", "कर्मचारी प्रबंधन", "उपकरण प्रबंधन"])

# 1. डैशबोर्ड
if choice == "डैशबोर्ड":
    st.title("📊 डैशबोर्ड & एक्सपायरी अलर्ट")
    df_equip = pd.read_sql("SELECT * FROM equipment", conn)
    if not df_equip.empty:
        df_equip['exp_date'] = pd.to_datetime(df_equip['exp_date'])
        alert_df = df_equip[df_equip['exp_date'] <= (datetime.now() + pd.Timedelta(days=10))]
        st.subheader("⚠️ 10 दिन में एक्सपायर होने वाले उपकरण")
        st.dataframe(alert_df.style.set_properties(**{'background-color': '#ffcccc'}), use_container_width=True)
        csv = df_equip.to_csv(index=False).encode('utf-8')
        st.download_button("📥 पूरी रिपोर्ट डाउनलोड करें", csv, "report.csv", "text/csv")

# 2. कर्मचारी प्रबंधन
elif choice == "कर्मचारी प्रबंधन":
    st.title("👤 कर्मचारी प्रबंधन")
    with st.form("emp_form"):
        name = st.text_input("नाम"); phone = st.text_input("मोबाइल"); addr = st.text_area("पता")
        bank = st.text_input("बैंक"); acc = st.text_input("अकाउंट नंबर"); ifsc = st.text_input("IFSC")
        if st.form_submit_button("सेव करें"):
            conn.execute("INSERT INTO employees (name, phone, address, bank_name, acc_no, ifsc) VALUES (?,?,?,?,?,?)", (name, phone, addr, bank, acc, ifsc))
            conn.commit(); st.success("डेटा सेव हुआ!")
    st.dataframe(pd.read_sql("SELECT * FROM employees", conn))

# 3. उपकरण प्रबंधन
elif choice == "उपकरण प्रबंधन":
    st.title("🚜 उपकरण प्रबंधन")
    with st.form("equip_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("उपकरण नाम"); model = c2.text_input("मॉडल")
        reg = c1.text_input("Reg No"); exp = c2.date_input("एक्सपायरी डेट")
        if st.form_submit_button("जोड़ें"):
            conn.execute("INSERT INTO equipment (name, model, reg_no, exp_date) VALUES (?,?,?,?)", (name, model, reg, exp))
            conn.commit(); st.success("उपकरण जोड़ा गया!")
    st.dataframe(pd.read_sql("SELECT * FROM equipment", conn))

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()