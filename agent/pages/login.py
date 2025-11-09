import streamlit as st
import sqlite3

def show():
    st.set_page_config(page_title="Login | Incident IQ", page_icon="🔐", layout="centered")
    st.title("🔐 Login to Incident IQ")

    email = st.text_input("Email", value="root@example.com")
    password = st.text_input("Password", type="password", value="5012f5182061c46e57859cf617128c6f70eddfba4db27772bdede5a039fa7085")

    if st.button("Login"):
        conn = sqlite3.connect("incident_iq.db")
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()
        conn.close()

        if user:
            st.session_state.user_logged_in = True
            st.session_state.username = user[1]
            st.success("✅ Login successful")
            st.rerun()  # redirect to dashboard
        else:
            st.error("❌ Invalid email or password")
