import streamlit as st
# EDA Pkgs
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from datetime import datetime
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

if 'session_state' not in st.session_state:
    st.session_state.session_state = {}

#import function file 
from suggestion_fn import *

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
    
                            # Display the cart items
                            if cart_items:
                                cart_df = pd.DataFrame(cart_items, columns=["Username", "Item Name", "Category" ,"Total Price", "Quantity"])
                                st.write("**Cart Items:**")
        
                                # Iterate through the cart items and display them individually
                                for index, row in cart_df.iterrows():
                                    st.write(f"**Item Name:** {row['Item Name']}")
                                    st.write(f"**Category:** {row['Category']}")
                                    st.write(f"**Total Price:** ${row['Total Price']:.2f}")
                                    # Add a number input field for quantity
                                    new_quantity = st.slider('Quantity:', min_value=1, max_value=10, value=row['Quantity'], key=f'quantity_{index}')
                                    # If the quantity is updated, update the DataFrame
                                    if new_quantity != row['Quantity']:
                                        cart_df.at[index, 'Quantity'] = new_quantity
                                        # Update cart with new quantities
                                        update_cart_quantities(username, cart_df)
                                    # Add a button to remove the item from the cart
                                    if st.button(f'Remove : {row["Item Name"]}', key=f'remove_{index}'):
                                        item_name = row['Item Name']
                                        delete_item_from_cart(username, item_name)
                                    st.write("---")  # Add a separator between items

                                # Calculate and display the subtotal
                                subtotal = calculate_cart_subtotal(username)
                                if subtotal is not None:
                                    st.write(f"*Subtotal:* ${subtotal:.2f}")
                                else:
                                    st.write("Items not available")                              

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

                                    if make_purchase(username):
                                        add_payment_details(account_number, expiration_month, expiration_year, cvv, purchase_date)
                                        conn.commit()


                                        st.success("Your purchase has been completed.")
                                        # st.experimental_rerun()  # Refresh the page to reflect the updated cart
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

                                # Convert 'Purchase Date' to datetime and round it to the nearest minute
                                purchase_df['Purchase Date'] = pd.to_datetime(purchase_df['Purchase Date']).dt.round('min')

                                # Group purchases by purchase date and time
                                grouped_purchases = purchase_df.groupby('Purchase Date')

                                # Display purchases for each group
                                for purchase_time, group in grouped_purchases:
                                    with st.expander(f"Purchases made at {purchase_time}:"):
                                        # Select specific columns
                                        display_df = group[['User Name', 'Item Name', 'Category', 'Quantity', 'Total Price']]
                                        # Convert to list of dictionaries
                                        purchases_list = display_df.to_dict('records')
                                        for purchase in purchases_list:
                                            st.write(f"**User Name:** {purchase['User Name']}")
                                            st.write(f"**Item Name:** {purchase['Item Name']}")
                                            st.write(f"**Category:** {purchase['Category']}")
                                            st.write(f"**Quantity:** {purchase['Quantity']}")
                                            st.write(f"**Total Price:** {purchase['Total Price']}")

                                            # Add a rating input field for each item
                                            rating = st.slider(label='Rate this item (1-10)', min_value=1, max_value=10, key=f"{purchase['Item Name']}_{purchase_time}_{purchase['Total Price']}_rating")  # Updated key

                                            # Save the rating in the item_rating table
                                            if st.button(f'Submit Rating : for {purchase["Item Name"]}_{purchase["Total Price"]}_{purchase_time}'):
                                                create_item_rating_table()
                                                save_item_rating(username, purchase['Item Name'], rating)
                                                st.success("Thank you for rating our product.")

                                            st.write("---")

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

                                if st.button("Don't press"):
                                    export_to_csv()
                                
                                # Preprocess the data
                                def preprocess_data(data):
                                    user_items = defaultdict(list)
                                    for row in data:
                                        _,user_name,  _, item_name, _, _, _, _ = row
                                        user_items[user_name].append(item_name)
                                    return user_items

                                #Build recommendation model
                                def build_recommendation_model(user_items):
                                    all_items = set()
                                    for items in user_items.values():
                                        all_items.update(items)

                                    item_to_index = {item: i for i, item in enumerate(all_items)}

                                    user_item_matrix = []
                                    for user, items in user_items.items():
                                        user_vector = [0] * len(all_items)
                                        for item in items:
                                            user_vector[item_to_index[item]] = 1
                                        user_item_matrix.append(user_vector)

                                    user_item_matrix = np.array(user_item_matrix)

                                    similarity_matrix = cosine_similarity(user_item_matrix, user_item_matrix)

                                    return similarity_matrix, item_to_index,user_item_matrix

                                #Generate recommendations for a specific user
                                def get_recommendations(user_id, user_items, similarity_matrix, item_to_index,user_item_matrix):
                                    user_index = list(user_items.keys()).index(user_id)
                                    user_similarities = similarity_matrix[user_index]
                                    similar_users_indices = user_similarities.argsort()[::-1][1:]  

                                    recommendations = set()
                                    for idx in similar_users_indices:
                                        for item_idx, val in enumerate(user_item_matrix[idx]):
                                            if val == 1 and item_idx not in user_item_matrix[user_index]:
                                                recommendations.add(item_idx)

                                    recommended_items = [item for item, idx in item_to_index.items() if idx in recommendations]

                                    return recommended_items


                                
                                def get_recommendation_details(recommendations):
                                    details = []
                                    for item_idx in recommendations:
                                        # Get item details from the corresponding CSV file
                                        category = "Men's"  # Assuming it's Men's category
                                        if category == "Men's":
                                            df_sugg = pd.read_csv("data/men.csv")
                                        elif category == "Women's":
                                            df_sugg = pd.read_csv("data/women.csv")
                                        elif category == "Children's":
                                            df_sugg = pd.read_csv("data/kids.csv")

                                        # Extract relevant details (image_url, price)
                                        item_details = df_sugg.iloc[item_idx]
                                        image_url = item_details['image_url']
                                        price = item_details['price']

                                        details.append((image_url, price))

                                    return details
                                
                                def display_recommendations_grid(details):
                                    for image_url, price in details:
                                        st.image(image_url, caption=f'Price: ${price}', use_column_width=True)
                                                                                                
                                data = view_purchase_history(username)

                                user_items = preprocess_data(data)
                                similarity_matrix, item_to_index,user_item_matrix = build_recommendation_model(user_items)
                                
                                
                                # Get recommendations for a user
                                recommendations = get_recommendations(username, user_items, similarity_matrix, item_to_index,user_item_matrix)
                                
        
                                # Step 5: Get recommendation item details
                                details = get_recommendation_details(recommendations)

                                # Step 6: Display recommendations in grid pattern
                                st.title(f"Recommended Items for {username}")
                                display_recommendations_grid(details)

                                def display_matrix(matrix):
                                    for row in matrix:
                                        print(row)

                                # Assuming user_item_matrix is defined
                                display_matrix(user_item_matrix)


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
                        
                            #convert data types


                             

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
                             item_data = view_all_inventry_items()
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

                             result = view_all_inventry_items()
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

                             if st.button("Update Item"):
                                edit_item(newitem_category,newitem_sub_category,newitem_name,newitem_price,newitem_discount,newitem_isnew,newitem_brand,
			                                newitem_color_varient_1,newitem_color_varient_2,newitem_image,get_category,get_subcategory,get_name,get_price,
			                                get_discount,get_isnew,get_brand,get_colour1,get_colour2,get_url)
                                st.success("Sucessfully Updated {}".format(newitem_name))

                             result2 = view_all_inventry_items()
                             df2 = pd.DataFrame(result2,columns=["category", "subcategory", "name", "price", "discount", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             with st.expander("Updated Data"):
                                st.dataframe(df2)

                             



                        elif task == "Delete Item":
                             st.subheader("Delete items")

                             result = view_all_inventry_items()
                             df = pd.DataFrame(result,columns=["category", "subcategory", "name", "price", "discount", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             with st.expander("Current Data"):
                                st.dataframe(df)

                             list_of_item = [i[0] for i in view_unique_item()]

                             selected_item = st.selectbox("Items to Delete",list_of_item)

                             st.warning("Do you want to delete {} ".format(selected_item))
                             if st.button("Delete Task"):
                                delete_item(selected_item)
                                st.success("Task has been sucessfully deleted")

                             result2 = view_all_inventry_items()
                             df2 = pd.DataFrame(result2,columns=["category", "subcategory", "name", "price", "discount", "likes", "isnew", "brand", "colour1", "colour2", "image_url"])
                             with st.expander("New Data"):
                                st.dataframe(df2)


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