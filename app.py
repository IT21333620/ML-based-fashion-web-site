import streamlit as st
# EDA Pkgs
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

# DB
from db_fxns import *

# Security
# passlib, hashlib, bcrypt, scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

# Reading Time

# Layout Templates

def main():
    """A Simple CRUD Blog"""
    html_temp = """
        <div style="background-color:{};padding:10px;border-radius:10px">
        <h1 style="color:{};text-align:center;">The Fashion Store</h1>
        </div>
        """
    st.markdown(html_temp.format('royalblue', 'white'), unsafe_allow_html=True)

    menu = ["Home", "SignUp", "Login", "View Items", "Cart", "Suggestions"]
    choice = st.sidebar.selectbox("Menu", menu)


    if choice == "Home":
        st.subheader("Home")

        defi_para = """
            <div style="background: linear-gradient(to bottom right, #FFA500, #FF6347); color: #000; padding: 20px; border-radius: 10px; font-weight: bolder;">
                <h2>About Fashion  Store</h2>
                <p>This web app is meticulously crafted for fashion retail store, offering an immersive and delightful shopping experience for users.
                  Explore our extensive collection of high-quality fashion products, from clothing to accessories, 
                  and effortlessly make purchases online. Our innovative Smart Suggestions feature harnesses 
                  the power of AI to recommend stylish dress combinations that perfectly match your budget and taste.</p>
            </div>
        """

        st.markdown(defi_para,unsafe_allow_html=True)

    elif choice == "SignUp":

        st.subheader("Create A New Account")
        new_name = st.text_input("Name")
        new_age = st.number_input("Age", min_value=1, step=1, format="%d")
        new_gender = st.selectbox("Gender",['Male','Female'])
        new_user = st.text_input("User name")
        new_password = st.text_input("Password", type='password')
        new_usertype = st.selectbox("Type", ['User'], key="usertype_selectbox",disabled=True)


        if st.button("Signup"):
            create_usertable()
            add_userdata(new_name,new_age,new_gender,new_user,make_hashes(new_password),new_usertype)
            st.success("Account created sucessfully")
            

    elif choice == "View Items":
        st.subheader("Items for Sale")

    elif choice == "Cart":
        st.subheader("Your cart")

    elif choice == "Login":
        st.subheader("Logged In")
        st.sidebar.text("Login as User")
        username = st.sidebar.text_input("Username",key='user_username')
        password = st.sidebar.text_input("Password", type='password',key='user_password')

        st.sidebar.text("Login as Admin")
        Ausername = st.sidebar.text_input("Username",key='admin_username')
        Apassword = st.sidebar.text_input("Password", type='password',key='admin_password')

    elif choice == "Suggestions":
        st.subheader("Smart Suggestions")

if __name__ == '__main__':
    main()
