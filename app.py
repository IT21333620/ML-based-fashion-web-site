import streamlit as st
# EDA Pkgs
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

# DB
from db_fxns import *
from db_cart import *

# Security
# passlib, hashlib, bcrypt, scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False


def main():
    """A Simple CRUD Blog"""
    html_temp = """
        <div style="background-color:{};padding:10px;border-radius:10px">
        <h1 style="color:{};text-align:center;">The Fashion Store</h1>
        </div>
        """
    st.markdown(html_temp.format('royalblue', 'white'), unsafe_allow_html=True)

    menu = ["Home", "SignUp", "Login"]
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
            

    elif choice == "Login":

        username = st.sidebar.text_input("Username", key='user_username')
        password = st.sidebar.text_input("Password", type='password', key='user_password')

        if st.sidebar.checkbox("User Login"):
            hashed_pwd = make_hashes(password)
        
        
            result = login_user(username,check_hashes(password,hashed_pwd))

            if result:
                user_type = get_user_type(username)
                if user_type:

                    if user_type == "User":
                        st.subheader("Logged In")
                        st.success("Logged In as User :: {}".format(username))
                        task = st.selectbox("Welcome,Choose what to do",['Market place','Cart','Smart Suggestions'])

                        if task == "Market place":
                            st.subheader("This is marketplace")
                            task1 = st.selectbox("Select Category", ["Women's", "Men's", "Children's"])
                            if task1 == "Women's":
                                df = pd.read_csv("women.csv")
                                st.subheader("Women's Clothing")

                                # Optionally, add a button to clear the cart
                                if st.button('Clear Cart'):
                                    # Clear the cart table in the database
                                    c.execute("DELETE FROM cart")
                                    conn.commit()

                                # Display the dataset with images in rows of four items each
                                st.write('**Products:**')

                                num_items = len(df)
                                items_per_row = 4

                                for start_index in range(0, num_items, items_per_row):
                                    end_index = min(start_index + items_per_row, num_items)
                                    items_in_current_row = df[start_index:end_index]

                                    # Create a Streamlit row to display items in a horizontal line
                                    cols = st.columns(4)

                                    for index, row in items_in_current_row.iterrows():
                                        with cols[index % 4]:
                                            st.image(row['image_url'], caption=row['name'][:15] + '...' if len(row['name']) > 15 else row['name'], use_column_width=True)
                                            # Display the price below the image
                                            st.write(f"Price: ${row['current_price']:.2f}")


                                            # Add an input field for quantity
                                            quantity = st.number_input('Quantity', min_value=1, value=1, key=f'quantity_{index}')

                                            # Add the "Add to Cart" button inside a custom container div
                                            with st.container():
                                                if st.button(f'Add to Cart', key=f'add_button_{index}'):
                                                    create_cart_table()
                                                    c.execute("INSERT INTO cart (item_name, price, quantity) VALUES (?, ?, ?)", (row['name'], row['current_price'], quantity))
                                                    conn.commit()
                                                st.write("")
                                                st.write("")
                                                st.write("")

                            elif task1 == "Men's":
                                df = pd.read_csv("men.csv")
                                st.subheader("Men's Clothing")

                                # Optionally, add a button to clear the cart
                                if st.button('Clear Cart'):
                                    # Clear the cart table in the database
                                    c.execute("DELETE FROM cart")
                                    conn.commit()

                                # Display the dataset with images in rows of four items each
                                st.write('**Products:**')

                                num_items = len(df)
                                items_per_row = 4

                                for start_index in range(0, num_items, items_per_row):
                                    end_index = min(start_index + items_per_row, num_items)
                                    items_in_current_row = df[start_index:end_index]

                                    # Create a Streamlit row to display items in a horizontal line
                                    cols = st.columns(4)

                                    for index, row in items_in_current_row.iterrows():
                                        with cols[index % 4]:
                                            st.image(row['image_url'], caption=row['name'][:15] + '...' if len(row['name']) > 15 else row['name'], use_column_width=True)
                                            # Display the price below the image
                                            st.write(f"Price: ${row['current_price']:.2f}")

                                            # Add an input field for quantity
                                            quantity = st.number_input('Quantity', min_value=1, value=1, key=f'quantity_{index}')

                                            # Add the "Add to Cart" button inside a custom container div
                                            with st.container():
                                                if st.button(f'Add to Cart', key=f'add_button_{index}'):
                                                    create_cart_table()
                                                    c.execute("INSERT INTO cart (item_name, price, quantity) VALUES (?, ?, ?)", (row['name'], row['current_price'], quantity))
                                                    conn.commit()
                                                st.write("")
                                                st.write("")
                                                st.write("")

                            elif task1 == "Children's":
                                df = pd.read_csv("kids.csv")
                                st.subheader("Men's Clothing")

                                # Optionally, add a button to clear the cart
                                if st.button('Clear Cart'):
                                    # Clear the cart table in the database
                                    c.execute("DELETE FROM cart")
                                    conn.commit()

                                # Display the dataset with images in rows of four items each
                                st.write('**Products:**')

                                num_items = len(df)
                                items_per_row = 4

                                for start_index in range(0, num_items, items_per_row):
                                    end_index = min(start_index + items_per_row, num_items)
                                    items_in_current_row = df[start_index:end_index]

                                    # Create a Streamlit row to display items in a horizontal line
                                    cols = st.columns(4)

                                    for index, row in items_in_current_row.iterrows():
                                        with cols[index % 4]:
                                            st.image(row['image_url'], caption=row['name'][:15] + '...' if len(row['name']) > 15 else row['name'], use_column_width=True)
                                            # Display the price below the image
                                            st.write(f"Price: ${row['current_price']:.2f}")

                                            # Add an input field for quantity
                                            quantity = st.number_input('Quantity', min_value=1, value=1, key=f'quantity_{index}')

                                            # Add the "Add to Cart" button inside a custom container div
                                            with st.container():
                                                if st.button(f'Add to Cart', key=f'add_button_{index}'):
                                                    create_cart_table()
                                                    c.execute("INSERT INTO cart (item_name, price, quantity) VALUES (?, ?, ?)", (row['name'], row['current_price'], quantity))
                                                    conn.commit()
                                                st.write("")
                                                st.write("")
                                                st.write("")


                        elif task == "Cart":
                             st.subheader("This is cart")


                        if task == "Smart Suggestions":
                             st.subheader("This is ml suggestions")




                    elif user_type == "Admin":
                        st.subheader("Logged In")
                        st.success("Logged In as Admin :: {}".format(username))
                        task = st.selectbox("Welcome,Choose what to do",['Add Item','View Added Item','Update Item','Delete Item','Forcasts'])

                        if task == "Add Item":
                             st.subheader("Add Desired Item")

                             col1,col2 = st.columns(2)

                             with col1:
                                  item_category = st.selectbox("Choose category",['Men','Women'])
                                  item_sub_category = st.text_input("Sub category")
                                  item_name = st.text_input("Item Name")
                                  item_price = st.number_input("Item Price",min_value=1.0)
                                  item_discount = st.slider("Item Discount",min_value=0.0,max_value=100.0)

                             with col2:
                                  item_brand = st.text_input("Item Brand")
                                  item_color_varient_1 = st.text_input("Colour Varient 1")
                                  item_color_varient_2 = st.text_input("Colour Varient 2")
                                  item_image = st.text_area("Image Link")
                            
                             if st.button("Add Item"):
                                  create_item_table()
                                  add_item_data(item_category,item_sub_category,item_name,item_price,item_discount,
                                                0,"True",item_brand,item_color_varient_1,item_color_varient_2,item_image)
                                  st.success("Item {}'s {} added sucessfully".format(item_category,item_sub_category))
                             



                        elif task == "View Added Item":
                             st.subheader("View added item")
                             item_data = view_all_items()
                             df = pd.DataFrame(item_data,columns=["category", "subcategory", "name", "price", "discount", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             
                             num_items = len(df)
                             items_per_row = 4

                             for start_index in range(0, num_items, items_per_row):
                                end_index = min(start_index + items_per_row, num_items)
                                items_in_current_row = df[start_index:end_index]

                                cols = st.columns(4)

                                for index, row in items_in_current_row.iterrows():
                                    with cols[index % 4]:
                                        caption_text = f"{row['category']} - {row['subcategory']} - {row['name']}"
                                        st.image(row['image_url'], caption=caption_text, use_column_width=True)









                        elif task == "Update Item":
                             st.subheader("Update items")

                             result = view_all_items()
                             df = pd.DataFrame(result,columns=["category", "subcategory", "name", "price", "discount", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             with st.expander("Current Data"):
                                st.dataframe(df)

                             list_of_item = [i[0] for i in view_unique_item()]
                             selected_item = st.selectbox("Items to Edit",list_of_item)

                             selected_result = get_item(selected_item)

                             if selected_result:
                                  get_category = selected_result[0][0]
                                  get_subcategory = selected_result[0][1]
                                  get_name = selected_result[0][2]
                                  get_price = selected_result[0][3]
                                  get_discount = selected_result[0][4]
                                  get_isnew = selected_result[0][6]
                                  get_brand = selected_result[0][7]
                                  get_colour1 = selected_result[0][8]
                                  get_colour2 = selected_result[0][9]
                                  get_url = selected_result[0][10]

                             col1,col2 = st.columns(2)

                             with col1:
                                  newitem_category = st.selectbox(get_category,['Men','Women'])
                                  newitem_sub_category = st.text_input("Sub category",get_subcategory)
                                  newitem_name = st.text_input("Item Name",get_name)
                                  newitem_price = st.number_input("Item Price",get_price)
                                  newitem_discount = st.slider("Item Discount", 0.0, 100.0, get_discount)

                             with col2:
                                  newitem_isnew = st.selectbox(get_isnew,['True','False'])
                                  newitem_brand = st.text_input("Item Brand",get_brand)
                                  newitem_color_varient_1 = st.text_input("Colour Varient 1",get_colour1)
                                  newitem_color_varient_2 = st.text_input("Colour Varient 2",get_colour2)
                                  newitem_image = st.text_area("Image Link",get_url)

                             if st.button("Update Task"):
                                edit_item(newitem_category,newitem_sub_category,newitem_name,newitem_price,newitem_discount,newitem_isnew,newitem_brand,
			                                newitem_color_varient_1,newitem_color_varient_2,newitem_image,get_category,get_subcategory,get_name,get_price,
			                                get_discount,get_isnew,get_brand,get_colour1,get_colour2,get_url)
                                st.success("Sucessfully Updated {}".format(newitem_name))

                             result2 = view_all_items()
                             df2 = pd.DataFrame(result2,columns=["category", "subcategory", "name", "price", "discount", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             with st.expander("Updated Data"):
                                st.dataframe(df2)

                             



                        elif task == "Delete Item":
                             st.subheader("Delete items")


                        elif task == "Forcasts":
                             st.subheader("View sales forcasts")
                             

                    else:
                        st.error("Unknown user type")
                else:
                    st.error("Failed to retrieve user type")
            else:
                st.error("Login failed. Please check your credentials.")

        

if __name__ == '__main__':
    main()
