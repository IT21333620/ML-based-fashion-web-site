import streamlit as st
# EDA Pkgs
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import math
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.preprocessing import LabelEncoder
import sqlite3

if 'session_state' not in st.session_state:
    st.session_state.session_state = {}

#global variables 
global df_sugg

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
                        
                        task = st.selectbox("Welcome, Choose what to do",['Market place','Cart','View Purchase History','Smart Suggestions'])

                        if task == "Market place":
                            st.subheader("This is marketplace")
                            task1 = st.selectbox("Select Category", ["Women's", "Men's", "Children's"])
                            if task1 == "Women's":
                                df = pd.read_csv("data/women.csv")
                                # Remove rows with null values in the specified columns
                                df = df.dropna(subset=["name", "variation_0_image", "current_price", "subcategory"])

                                substring_to_remove = "https://imgaz1.chiccdn.com/thumb/view/oaupload/ser1"

                                # Use boolean indexing to filter out rows containing the substring
                                df = df[~df['variation_0_image'].str.contains(substring_to_remove)]

                                page_size = 24
                                page_number = st.sidebar.number_input("Page Number", min_value=1, value=1)

                                # Calculate the start and end indices for the current page
                                start_index = (page_number - 1) * page_size
                                end_index = start_index + page_size

                                # Slice the dataset for the current page
                                current_page_df = df[start_index:end_index]

                                # Display the dataset with images for the current page
                                st.subheader("Men's Clothing")
                                st.write('**Products (Page {}):**'.format(page_number))

                                # Create a Streamlit row to display items in a horizontal line
                                cols = st.columns(4)

                                  
                                min_image_height = 10 

                                for index, row in enumerate(current_page_df.iterrows()):
                                    row_index, row_data = row  # Unpack the row data
                                    with cols[index % 4]:
                                        st.image(row_data['image_url'], 
                                            caption=row_data['name'][:15] + '...' if len(row_data['name']) > 15 else row_data['name'], 
                                            use_column_width=True ,  # Maintain column width
                                            output_format='JPEG')

                                    
                                        st.markdown(f'<div style="min-height: {min_image_height}px;"></div>', unsafe_allow_html=True)

                                        # Display the price below the image
                                        st.write(f"Price: ${row_data['current_price']:.2f}")

                                        # Add an input field for quantity
                                        quantity = st.number_input('Quantity', min_value=1, value=1, key=f'quantity_{row_index}')
                                        total_price = row_data['current_price'] * quantity

                                        # Add the "Add to Cart" button inside a custom container div
                                        with st.container():
                                            if st.button(f'Add to Cart', key=f'add_button_{row_index}'):
                                                create_cart_table()
                                                c.execute("INSERT INTO cart (user_name, category, item_name, price, total_price, quantity) VALUES (?, ?, ?, ?, ?, ?)", (username, task1, row_data['name'], row_data['current_price'], total_price, quantity))
                                                conn.commit()
                                            st.write("")
                                            st.write("")
                                            st.write("")

                                # Create a "Load More" button to fetch the next page
                                if end_index < len(df):
                                    st.sidebar.button("Load More")

                            elif task1 == "Men's":
                                df = pd.read_csv("data/men.csv")
                                # Remove rows with null values in the specified columns
                                df = df.dropna(subset=["name", "variation_0_image", "current_price", "subcategory"])

                                substring_to_remove = "https://imgaz1.chiccdn.com/thumb/view/oaupload/ser1"

                                # Use boolean indexing to filter out rows containing the substring
                                df = df[~df['variation_0_image'].str.contains(substring_to_remove)]

                                page_size = 24
                                page_number = st.sidebar.number_input("Page Number", min_value=1, value=1)

                                # Calculate the start and end indices for the current page
                                start_index = (page_number - 1) * page_size
                                end_index = start_index + page_size

                                # Slice the dataset for the current page
                                current_page_df = df[start_index:end_index]

                                # Display the dataset with images for the current page
                                st.subheader("Men's Clothing")
                                st.write('**Products (Page {}):**'.format(page_number))

                                # Create a Streamlit row to display items in a horizontal line
                                cols = st.columns(4)

                                  
                                min_image_height = 10 

                                for index, row in enumerate(current_page_df.iterrows()):
                                    row_index, row_data = row  # Unpack the row data
                                    with cols[index % 4]:
                                        st.image(row_data['image_url'], 
                                            caption=row_data['name'][:28] + '...' if len(row_data['name']) > 28 else row_data['name'], 
                                            use_column_width=True ,  # Maintain column width
                                            output_format='JPEG')

                                    
                                        st.markdown(f'<div style="min-height: {min_image_height}px;"></div>', unsafe_allow_html=True)

                                        # Display the price below the image
                                        st.write(f"Price: ${row_data['current_price']:.2f}")

                                        # Add an input field for quantity
                                        quantity = st.number_input('Quantity', min_value=1, value=1, key=f'quantity_{row_index}')
                                        total_price = row_data['current_price'] * quantity

                                        # Add the "Add to Cart" button inside a custom container div
                                        with st.container():
                                            if st.button(f'Add to Cart', key=f'add_button_{row_index}'):
                                                create_cart_table()
                                                c.execute("INSERT INTO cart (user_name, category, item_name, price, total_price, quantity) VALUES (?, ?, ?, ?, ?, ?)", (username, task1, row_data['name'], row_data['current_price'], total_price, quantity))
                                                conn.commit()
                                            st.write("")
                                            st.write("")
                                            st.write("")

                                # Create a "Load More" button to fetch the next page
                                if end_index < len(df):
                                    st.sidebar.button("Load More")

                            elif task1 == "Children's":
                                df = pd.read_csv("data/kids.csv")
                                # Remove rows with null values in the specified columns
                                df = df.dropna(subset=["name", "variation_0_image", "current_price", "subcategory"])

                                substring_to_remove = "https://imgaz1.chiccdn.com/thumb/view/oaupload/ser1"

                                # Use boolean indexing to filter out rows containing the substring
                                df = df[~df['variation_0_image'].str.contains(substring_to_remove)]

                                page_size = 24
                                page_number = st.sidebar.number_input("Page Number", min_value=1, value=1)

                                # Calculate the start and end indices for the current page
                                start_index = (page_number - 1) * page_size
                                end_index = start_index + page_size

                                # Slice the dataset for the current page
                                current_page_df = df[start_index:end_index]

                                # Display the dataset with images for the current page
                                st.subheader("Men's Clothing")
                                st.write('**Products (Page {}):**'.format(page_number))

                                # Create a Streamlit row to display items in a horizontal line
                                cols = st.columns(4)

                                  
                                min_image_height = 10 

                                for index, row in enumerate(current_page_df.iterrows()):
                                    row_index, row_data = row  # Unpack the row data
                                    with cols[index % 4]:
                                        st.image(row_data['image_url'], 
                                            caption=row_data['name'][:28] + '...' if len(row_data['name']) > 28 else row_data['name'], 
                                            use_column_width=True ,  # Maintain column width
                                            output_format='JPEG')

                                    
                                        st.markdown(f'<div style="min-height: {min_image_height}px;"></div>', unsafe_allow_html=True)

                                        # Display the price below the image
                                        st.write(f"Price: ${row_data['current_price']:.2f}")

                                        # Add an input field for quantity
                                        quantity = st.number_input('Quantity', min_value=1, value=1, key=f'quantity_{row_index}')
                                        total_price = row_data['current_price'] * quantity

                                        # Add the "Add to Cart" button inside a custom container div
                                        with st.container():
                                            if st.button(f'Add to Cart', key=f'add_button_{row_index}'):
                                                create_cart_table()
                                                c.execute("INSERT INTO cart (user_name, category, item_name, price, total_price, quantity) VALUES (?, ?, ?, ?, ?, ?)", (username, task1, row_data['name'], row_data['current_price'], total_price, quantity))
                                                conn.commit()
                                            st.write("")
                                            st.write("")
                                            st.write("")

                                # Create a "Load More" button to fetch the next page
                                if end_index < len(df):
                                    st.sidebar.button("Load More")


                        elif task == "Cart":
                            st.subheader("This is cart")
                            
                            # Call the view_all_items() function to retrieve cart items
                            cart_items = view_all_items(username)
                            # Display the cart items in a table
                            if cart_items:
                                cart_df = pd.DataFrame(cart_items, columns=["Username", "Item Name", "Category" ,"Total Price", "Quantity"])
                                st.write("**Cart Items:**")
                                st.dataframe(cart_df)

                                #Calculate and display the subtotal
                                subtotal = calculate_cart_subtotal(username)
                                st.write(f"*Subtotal:* ${subtotal:.2f}")
                            else:
                                st.write("Your cart is empty.")

                            with st.form('Payment Detalis'):
                                account_number = st.number_input('Account Number', 0,)
                                col1, col2 = st.columns(2)  # Create two columns here
                                with col1:
                                    expiration_month = st.selectbox('Experation Date', range(1, 13))
                                with col2:
                                    expiration_year = st.selectbox('Experation Month', range(2023, 2030))
                                cvv = st.number_input('cvv', min_value=100)

                                # Add a button to make the purchase
                                if st.form_submit_button('Make Purchase'):
                                    purchase_date = datetime.today().strftime('%Y-%m-%d')
                                    add_payment_details(account_number, expiration_month, expiration_year, cvv, purchase_date)
                                    
                                    # Clear the form fields after successful submission
                                    account_number, expiration_month, expiration_year, cvv = '', None, None, None
                                    cart_items = get_cart_items(username)

                                    if make_purchase(username):
                                        add_payment_details(account_number, expiration_month, expiration_year, cvv, purchase_date)
                                        
                                          
                                        # Process each item in the cart
                                        for cart_item in cart_items:
                                            item_name = cart_item[0]
                                            quantity = cart_item[1] 

                                            # Find the corresponding item in itemstable
                                            item = get_item_by_name(item_name)
                                            # Calculate the updated quantity
                                            updated_quantity = item['quantity'] - quantity

                                            # Update the quantity in itemstable
                                            update_item_quantity(item_name, updated_quantity)

                                            # Remove the item from the cart
                                            remove_item_from_cart(username, item_name)

                                        conn.commit()
                                        st.success("Your purchase has been completed.")
                                    else:
                                        st.warning("Your cart is empty. Add items to your cart before making a purchase.")

                            # Optionally, add a button to clear the cart
                            if st.button('Clear Cart'):
                                delete_cart(username)
                                st.success("Your cart has been cleared.")
                                st.experimental_rerun()

                        elif task == "View Purchase History":
                            st.subheader("View Purchase History")

                            # Call the view_purchase_history function to retrieve purchase history for the user
                            purchase_history = view_purchase_history(username)

                            if purchase_history:
                                # Convert the purchase history to a DataFrame for better display
                                purchase_df = pd.DataFrame(purchase_history, columns=["ID", "User Name", "Category", "Item Name", "Price", "Total Price", "Quantity", "Purchase Date"])
                                st.dataframe(purchase_df)

                            else:
                                st.write("No purchase history available for this user.")


                        if task == "Smart Suggestions":
                            #########################################################################
                            st.title("Suggestions")
                            sugg_intro = """
                                <div style="background: linear-gradient(to bottom right, #FFA500, #FF6347); color: #000; padding: 20px; border-radius: 10px; font-weight: bolder;">
                                    <p>This is a feature that allows users to get their preferred clothing without seaming the whole website. You can get suggestions from an item that
                                      is in your cart or based on your past purchases. User-based suggestions will suggest an item that may not be similar, but you may have an interest 
                                      but item-based suggestions will give you similar items. You are free to find your favorite cloth by this feature..</p>
                                </div>
                            """

                            st.markdown(sugg_intro,unsafe_allow_html=True)
                           
                            suggestion_type = st.radio("Select Suggestion type",["Item Base","User Base"])

                            if suggestion_type == "Item Base":
                                st.write("Item based")
                                orderitem = view_cart_item(username)
                                if orderitem:
                                    item_name = st.selectbox("Match to", orderitem)
                                    dataset_type = viewCatogory(item_name)
                                    cleaned_string = dataset_type[0][0].strip("[]()")
                                    

                                    
                                    if cleaned_string =="Men's":
                                        df_sugg = pd.read_csv("data/men.csv")
                                    elif cleaned_string =="Women's":
                                        df_sugg = pd.read_csv("data/women.csv")
                                    elif cleaned_string =="Children's":
                                        df_sugg = pd.read_csv("data/kids.csv")
                                    
                                    item_cloumn = df_sugg[df_sugg['name']== item_name]

                                    if not item_cloumn.empty:
                                        item_cart = item_cloumn.iloc[0]['variation_0_image']
                                        st.write(f'<div style="display: flex; justify-content: center;"><img src="{item_cart}" width="300"></div>', unsafe_allow_html=True)

                                    #Remove un nessory cloumns from the data set 
                                    columns_to_display = ["subcategory", "name", "current_price", "discount", "likes_count", "is_new", "brand", "variation_0_color", "variation_1_color","variation_0_image"]
                                    item_df = df_sugg[columns_to_display].fillna("")

                                 
                                    df_sugg = df_sugg.dropna(subset=[ "variation_0_image"])

                                    item_df['content'] = item_df['subcategory'] + " " + item_df['brand'] + " " + item_df['variation_0_color'] + " " + item_df['variation_1_color'] 

                                    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
                                    tfidf_matrix = tfidf_vectorizer.fit_transform(item_df['content'])

                                    # Compute cosine similarity between items
                                    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

                                    def get_recommendations(item_name, max_price, min_discount, cosine_sim_matrix=cosine_sim):
                                        item_indices = []
                                        for idx, name in item_df[['name']].iterrows():
                                            if name['name'] == item_name:
                                                item_indices.append(idx)
                                        
                                        if not item_indices:
                                            return "Item not found in the dataset"
                                        
                                        idx = item_indices[0]
                                        sim_scores = list(enumerate(cosine_sim_matrix[idx]))
                                        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                                        
                                        # Filter recommendations based on price and discount constraints
                                        filtered_indices = []
                                        for i in range(1, len(sim_scores)):
                                            rec_idx = sim_scores[i][0]
                                            rec_price = item_df.loc[rec_idx, "current_price"]
                                            rec_discount = item_df.loc[rec_idx, "discount"]
                                            if rec_price <= max_price and rec_discount >= min_discount:
                                                filtered_indices.append(rec_idx)
                                            if len(filtered_indices) >= 10:
                                                break
                                        
                                        # Create a DataFrame with recommended items and selected attributes
                                        recommendations_df = item_df.loc[filtered_indices, ["name","current_price","brand","variation_0_color","variation_1_color","variation_0_image"]]
                                        return recommendations_df
                                    

                                    st.subheader("Add Constrains")
                                    max_price = st.slider("Maximum Price $", item_df["current_price"].min(), item_df["current_price"].max(), item_df["current_price"].mean())
                                    min_discount = st.number_input("Minimum Discount Rate (%)", value = round(item_df["discount"].mean(), 2), format="%f")

                                    recommendations = get_recommendations(item_name, max_price, min_discount)
                                    st.subheader("Recommended Items")
                            
                                    recommend_count = len(recommendations)
                                    no_of_col = 4

                                    for i in range(0, recommend_count, no_of_col):
                                        j = min(i + no_of_col, recommend_count)
                                        items_in_row = recommendations[i:j]  # Use recommendations DataFrame instead of df

                                        cols = st.columns(no_of_col)
                                        for col_index, row in enumerate(items_in_row.iterrows()):
                                            with cols[col_index]:
                                                st.image(
                                                    row[1]['variation_0_image'],  # Access the row data using row[1]
                                                    caption=f"{row[1]['name'][:37] + '...' if len(row[1]['name']) > 15 else row[1]['name']}",  # Access the row data using row[1]
                                                    
                                                    use_column_width=True
                                                )

                                                key = row[1]['name']

                                                if st.button(f"View", key=key):
                                                    # Store the selected item's information in the session_state
                                                    st.session_state.session_state['selected_item'] = {
                                                        'name': row[1]['name'],
                                                        'image': row[1]['variation_0_image'],
                                                        'price': row[1]['current_price'],
                                                        'brand':row[1]['brand'],
                                                        'color1':row[1]['variation_0_color'],
                                                        'color2':row[1]['variation_1_color']   
                                                        
                                                    }

                                else:
                                    st.write("No items in the cart.") 


                            elif suggestion_type == "User Base":
                                st.write("User based")
                            else:
                                st.write("Error.")


                            
                            

                            st.header("Selected Item Details")

                            # Check if any item details have been saved in session_state
                            if 'selected_item' in st.session_state.session_state:
                                selected_item = st.session_state.session_state['selected_item']
                                col1, col2 = st.columns([2, 3])  
                               
                                col1.image(selected_item['image'], caption=selected_item['name'], use_column_width=True)

                                col2.markdown(f"**<span style=' font-size: 25px;'>{selected_item['name']}** </span>", unsafe_allow_html=True)
                                col2.markdown(f"<span style=' font-size: 18px;'>**Brand:** {selected_item['brand']}</span>", unsafe_allow_html=True)
                                col2.markdown(f"<span style=' font-size: 18px;'>**Price:** $ {selected_item['price']}</span>", unsafe_allow_html=True)
                                col2.markdown(f"<span style=' font-size: 18px;'>**Available colors:** {selected_item['color1']}, {selected_item['color2']} </span>", unsafe_allow_html=True)
                                col2.markdown(f"<span style='margin: 40px;'>  </span>" , unsafe_allow_html=True)
                                quantity = col2.number_input('Quantity', min_value=1, value=1, )
                                total_price = selected_item['price'] * quantity
                               
                                if col2.button("Add to cart"):
                                    add_item_cart(username,cleaned_string,selected_item['name'],selected_item['price'],total_price,quantity )

                                
                            else:
                                st.write("No item selected. Click 'View' on an item to see its details.")     

                    elif user_type == "Admin":
                        st.subheader("Logged In")
                        st.success("Logged In as Admin :: {}".format(username))
                        task = st.selectbox("Welcome,Choose what to do",['Add Item','View Added Item','Update Item','Delete Item','Sales Forecast', 'Place Order', 'Order Delivery'])

                        if task == "Add Item":
                             st.subheader("Add Desired Item")

                             col1,col2 = st.columns(2)

                             with col1:
                                  item_category = st.selectbox("Choose category",['Men','Women'])
                                  item_sub_category = st.text_input("Sub category")
                                  item_name = st.text_input("Item Name")
                                  item_price = st.number_input("Item Price",min_value=1.0)
                                  item_discount = st.slider("Item Discount",min_value=0,max_value=100)
                                  item_quantity = st.number_input("Item Quantity",min_value=1)

                             with col2:
                                  item_brand = st.text_input("Item Brand")
                                  item_color_varient_1 = st.text_input("Colour Varient 1")
                                  item_color_varient_2 = st.text_input("Colour Varient 2")
                                  item_image = st.text_area("Image Link")
                            
                             if st.button("Add Item"):
                                  create_item_table()
                                  add_item_data(item_category,item_sub_category,item_name,item_price,item_discount,item_quantity,
                                                0,"True",item_brand,item_color_varient_1,item_color_varient_2,item_image)
                                  st.success("Item {}'s {} added sucessfully".format(item_category,item_sub_category))
                             



                        elif task == "View Added Item":
                             st.subheader("View added item")
                             item_data = view_all_inventry_items()
                             df = pd.DataFrame(item_data,columns=["category", "subcategory", "name", "price", "discount", "quantity","likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             
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

                             result = view_all_inventry_items()
                             df = pd.DataFrame(result,columns=["category", "subcategory", "name", "price", "discount", "quantity", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
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
                                  get_quantity = selected_result[0][5]
                                  get_isnew = selected_result[0][7]
                                  get_brand = selected_result[0][8]
                                  get_colour1 = selected_result[0][9]
                                  get_colour2 = selected_result[0][10]
                                  get_url = selected_result[0][11]

                             col1,col2 = st.columns(2)

                             with col1:
                                  newitem_category = st.selectbox(get_category,['Men','Women'])
                                  newitem_sub_category = st.text_input("Sub category",get_subcategory)
                                  newitem_name = st.text_input("Item Name",get_name)
                                  newitem_price = st.number_input("Item Price",get_price)
                                  newitem_discount = st.slider("Item Discount", 0, 100, get_discount)
                                  newitem_quantity = st.number_input("Item Quantity",get_quantity)

                             with col2:
                                  newitem_isnew = st.selectbox(get_isnew,['True','False'])
                                  newitem_brand = st.text_input("Item Brand",get_brand)
                                  newitem_color_varient_1 = st.text_input("Colour Varient 1",get_colour1)
                                  newitem_color_varient_2 = st.text_input("Colour Varient 2",get_colour2)
                                  newitem_image = st.text_area("Image Link",get_url)

                             if st.button("Update Item"):
                                edit_item(newitem_category,newitem_sub_category,newitem_name,newitem_price,newitem_discount,newitem_quantity,newitem_isnew,newitem_brand,
			                                newitem_color_varient_1,newitem_color_varient_2,newitem_image,get_category,get_subcategory,get_name,get_price,
			                                get_discount,get_isnew,get_brand,get_colour1,get_colour2,get_url)
                                st.success("Sucessfully Updated {}".format(newitem_name))

                             result2 = view_all_inventry_items()
                             df2 = pd.DataFrame(result2,columns=["category", "subcategory", "name", "price", "discount", "quantity", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             with st.expander("Updated Data"):
                                st.dataframe(df2)

                             



                        elif task == "Delete Item":
                             st.subheader("Delete items")

                             result = view_all_inventry_items()
                             df = pd.DataFrame(result,columns=["category", "subcategory", "name", "price", "discount", "quantity", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             with st.expander("Current Data"):
                                st.dataframe(df)

                             list_of_item = [i[0] for i in view_unique_item()]

                             selected_item = st.selectbox("Items to Delete",list_of_item)

                             st.warning("Do you want to delete {} ".format(selected_item))
                             if st.button("Delete Task"):
                                delete_item(selected_item)
                                st.success("Task has been sucessfully deleted")

                             result2 = view_all_inventry_items()
                             df2 = pd.DataFrame(result2,columns=["category", "subcategory", "name", "price", "discount", "quantity", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             with st.expander("New Data"):
                                st.dataframe(df2)


                        elif task == "Sales Forecast":
                            def load_data():
                                conn = sqlite3.connect('cart.db')
                                df = pd.read_sql('SELECT * FROM purchase_history', conn)
                                conn.close()
                                return df
                            
                            def get_item_quantity(item_name):
                                conn = sqlite3.connect('data.db')  # Adjust the database path as needed
                                c = conn.cursor()

                                # Execute a SQL query to retrieve the quantity of the selected item
                                c.execute("SELECT quantity FROM itemstable WHERE name = ?", (item_name,))
                                quantity = c.fetchone()

                                conn.close()

                                return quantity[0] if quantity else 0
                            
                            # Function to load the CSV file based on category
                            def load_category_data(category):
                                if category == "Women's":
                                    return 'data/women.csv'
                                elif category == "Men's":
                                    return 'data/men.csv'
                                elif category == "Children's":
                                    return 'data/kids.csv'
                                else:
                                    return None

                            def encode_item_name(df):
                                label_encoder = LabelEncoder()
                                df['item_name_encoded'] = label_encoder.fit_transform(df['item_name'])
                                return df

                            # Forecast sales using a simple linear regression model for a specific item
                            def forecast_sales_for_item(df, item_name, likes_count):
                                item_df = df[df['item_name'] == item_name]
                                item_df = item_df.groupby('item_name')['quantity'].sum().reset_index()

                                X = item_df[['quantity']]
                                y = item_df['quantity']

                                model = ExtraTreesRegressor(n_estimators=100, random_state=0)
                                model.fit(X, y)

                                return model, likes_count
                            
                            st.title('Clothing Store Sales Forecasting')
                            df = load_data()

                            item_name = st.selectbox('Select an item for sales forecasting:', df['item_name'].unique())

                            if item_name:
                                # Get the category from purchase_history
                                category = df.loc[df['item_name'] == item_name, 'category'].values[0]

                                # Load the appropriate CSV data based on the category
                                category_data_file = load_category_data(category)

                                if category_data_file:
                                    women_data = pd.read_csv(category_data_file)
                                    likes_count = women_data.loc[women_data['name'] == item_name, 'likes_count'].values[0]
                                    quantity_to_forecast = 2.33

                                    model, likes_count = forecast_sales_for_item(df, item_name, likes_count)

                                
                                    forecasted_total_sales = model.predict([[quantity_to_forecast]])[0] * quantity_to_forecast
                                    item_quantity = get_item_quantity(item_name)

                                    # Add Likes_count to forecasted_total_sales
                                    forecasted_total_sales += likes_count
                                    forecasted_total_sales = math.ceil(forecasted_total_sales)

                                    # Display the quantity of the selected item
                                    st.write(f'Quantity in Inventory: {item_quantity} Units')
                                    st.write("")

                                    st.write(f'Total Predicted Sales: {forecasted_total_sales} Units')
                                    st.write("")
                                    if forecasted_total_sales >= item_quantity:
                                        st.write('Status: Out of Stock')
                                        create_order_table()
                                        add_item_order(item_name,forecasted_total_sales)
                                    else:
                                        st.write('Status: In Stock')





                        elif task == "Place Order":
                            st.title('Place an order')
                            def load_data():
                                conn = sqlite3.connect('cart.db')
                                df = pd.read_sql('SELECT * FROM purchase_history', conn)
                                conn.close()
                                return df
                            
                            df = load_data()
                            item_name = st.selectbox('Select an item for sales forecasting:', df['item_name'].unique())

                            item_quantity = st.number_input("Item Quantity",min_value=1)

                            if st.button("Place Order"):
                                create_order_table()
                                add_item_order(item_name,item_quantity)
                                st.success("Order placed successfully")

                        elif task == "Order Delivery":
                            st.title('Order Details')

                            # Get a list of unique item names from the database
                            c.execute('SELECT DISTINCT item_name FROM ordertable')
                            item_names = [row[0] for row in c.fetchall()]

                            # Create a dropdown to select item_name
                            selected_item = st.selectbox('Select Item Name', item_names)

                            # Query the database for the quantity of the selected item
                            c.execute('SELECT item_quantity FROM ordertable WHERE item_name=?', (selected_item,))
                            quantity = c.fetchone()

                            # Display the quantity
                            if quantity:
                                st.write(f'Quantity for {selected_item}: {quantity[0]}')
                            else:
                                st.write(f'No quantity found for {selected_item}')

                            # Add a "Received" button
                            if st.button('Received'):
                                conn = sqlite3.connect('data.db')
                                c2 = conn.cursor()  # Use a different variable name here, like c2

                                c2.execute('SELECT quantity FROM itemstable WHERE name=?', (selected_item,))
                                current_quantity = c2.fetchone()

                                if current_quantity:
                                    # Calculate the new quantity by adding the received quantity
                                    new_quantity = current_quantity[0] + quantity[0]

                                    # Update the item_quantity in itemstable
                                    c2.execute('UPDATE itemstable SET quantity=? WHERE name=?', (new_quantity, selected_item))
                                    conn.commit()
                                    st.write(f'Item quantity updated successfully')

                                    c.execute('DELETE FROM ordertable WHERE item_name=?', (selected_item,))
                                    conn.commit()
                                    st.write(f'Record for {selected_item} has been removed from the order table.')
                                else:
                                    st.write(f'No item named {selected_item} found in itemstable')

                    else:
                        st.error("Unknown user type")
                else:
                    st.error("Failed to retrieve user type")
            else:
                st.error("Login failed. Please check your credentials.")

        

if __name__ == '__main__':
    main()