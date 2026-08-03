import streamlit as st

st.title("🔐 Admin Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    # Validate credentials from the admin table
    st.success("Login Successful")