#Core Package
from random import choice
import streamlit as st

#EDA Packages
import pandas as pd

def main():
    st.title("Add Item")

    menu = ["Add New Item","Item List","Update","Delete","About"]
    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Add New Item":
        st.subheadder("New Item")

    elif choice == "Item List":
        st.subheader("View Items")
    elif choice == "Update":
        st.subheader("Update Item")
    elif choice == "Delete":
        st.subheader("Delete Item")
        
    else:
        st.subheader("About")

if __name__ == ' main ':
    main()