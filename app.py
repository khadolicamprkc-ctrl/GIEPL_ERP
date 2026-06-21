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

# --- Login & Role Management ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

if not st.session_state.logged_in:
    st.title("🔐 GIEPL ERP Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.rerun()
        elif user == "staff1" and pwd == "staff123":
            st.session_state.logged_in = True
            st.session_state.user_role = "staff"
            st.rerun()
        else: st.error("गलत username या password!")
    st.stop()

# Sidebar
st.sidebar.title("🏗️ GIEPL ERP")
st.sidebar.write(f"यूजर: {st.session_state.user_role.upper()}")
choice = st.sidebar.selectbox("मेनू", ["डैशबोर्ड", "कर्मचारी प्रबंधन", "उपकरण प्रबंधन"])

# Developer Credit
st.sidebar.markdown("---")
st.sidebar.write("### 🏗️ Developed by: **Sajjan.exec**")
st.sidebar.write("© 2026 GIEPL Enterprises")

# --- Logic Starts Here ---
if choice == "डैशबोर्ड":
    st.title("📊 डैशबोर्ड")
    df_equip = pd.read_sql("SELECT * FROM equipment", conn)
    if not df_equip.empty:
        df_equip['exp_date'] = pd.to_datetime(df_equip['exp_date'])
        st.subheader("⚠️ 15 दिन में एक्सपायर होने वाले उपकरण")
        alert_df = df_equip[df_equip['exp_date'] <= (datetime.now() + pd.Timedelta(days=15))]
        st.dataframe(alert_df, use_container_width=True)

elif choice == "कर्मचारी प्रबंधन":
    st.title("👤 कर्मचारी प्रबंधन")
    if st.session_state.user_role == "admin":
        with st.form("emp_form"):
            name = st.text_input("नाम"); phone = st.text_input("मोबाइल"); addr = st.text_area("पता")
            bank = st.text_input("बैंक"); acc = st.text_input("अकाउंट नंबर"); ifsc = st.text_input("IFSC")
            if st.form_submit_button("सेव करें"):
                conn.execute("INSERT INTO employees (name, phone, address, bank_name, acc_no, ifsc) VALUES (?,?,?,?,?,?)", (name, phone, addr, bank, acc, ifsc))
                conn.commit(); st.success("डेटा सेव हुआ!")
    else:
        st.info("आप सिर्फ डेटा देख सकते हैं (एडमिन से संपर्क करें)")
    st.dataframe(pd.read_sql("SELECT * FROM employees", conn))

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