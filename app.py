import streamlit as st
# EDA Pkgs
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

if 'session_state' not in st.session_state:
    st.session_state.session_state = {}

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
                        
                        task = st.selectbox("Welcome, Choose what to do",['Market place','Cart','Smart Suggestions'])

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
                            df = pd.read_csv("data/men.csv")
                            

                            columns_to_display = ["subcategory", "name", "current_price", "discount", "likes_count", "is_new", "brand", "variation_0_color", "variation_1_color","variation_0_image"]
                            mens_df = df[columns_to_display].fillna("")

                            mens_df['content'] = mens_df['subcategory'] + " " + mens_df['brand'] + " " + mens_df['variation_0_color'] + " " + mens_df['variation_1_color'] 

                            tfidf_vectorizer = TfidfVectorizer(stop_words='english')
                            tfidf_matrix = tfidf_vectorizer.fit_transform(mens_df['content'])

                            # Compute cosine similarity between items
                            cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

                            def get_recommendations(item_name, max_price, min_discount, cosine_sim_matrix=cosine_sim):
                                item_indices = []
                                for idx, name in mens_df[['name']].iterrows():
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
                                    rec_price = mens_df.loc[rec_idx, "current_price"]
                                    rec_discount = mens_df.loc[rec_idx, "discount"]
                                    if rec_price <= max_price and rec_discount >= min_discount:
                                        filtered_indices.append(rec_idx)
                                    if len(filtered_indices) >= 10:
                                        break
                                
                                # Create a DataFrame with recommended items and selected attributes
                                recommendations_df = mens_df.loc[filtered_indices, ["name","current_price","brand","variation_0_color","variation_1_color","variation_0_image"]]
                                return recommendations_df


                            

                            item_name = "Pantalon homme 100% coton anti-rides Longueur"

                            st.title("Suggestions")
                            st.subheader("Add Constrains")
                            max_price = st.slider("Maximum Price $", mens_df["current_price"].min(), mens_df["current_price"].max(), mens_df["current_price"].mean())
                            min_discount = st.number_input("Minimum Discount Rate (%)", value = round(mens_df["discount"].mean(), 2), format="%f")


                            
                            recommendations = get_recommendations(item_name, max_price, min_discount)
                            st.write(recommendations)
                            st.subheader("Recommended Items")

                            recommend_count = len(recommendations)
                            no_of_col = 4
                            nno_of_rows = (recommend_count + no_of_col - 1) // no_of_col

                            for i in range(0, recommend_count, no_of_col):
                                j = min(i + no_of_col, recommend_count)
                                items_in_row = recommendations[i:j]  # Use recommendations DataFrame instead of df

                                cols = st.columns(no_of_col)
                                for col_index, row in enumerate(items_in_row.iterrows()):
                                    with cols[col_index]:
                                        st.image(
                                            row[1]['variation_0_image'],  # Access the row data using row[1]
                                            caption=f"{row[1]['name']}",  # Access the row data using row[1]
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

                            st.header("Selected Item Details")

                            # Check if any item details have been saved in session_state
                            if 'selected_item' in st.session_state.session_state:
                                selected_item = st.session_state.session_state['selected_item']
                                col1, col2 = st.columns([2, 3])  
                               
                                col1.image(selected_item['image'], caption=selected_item['name'], use_column_width=True)

                                col2.markdown(f"**<span style='color: blue; font-size: 25px;'>{selected_item['name']}** </span>", unsafe_allow_html=True)
                                col2.markdown(f"<span style='color: blue; font-size: 18px;'>**Brand:** {selected_item['brand']}</span>", unsafe_allow_html=True)
                                col2.markdown(f"<span style='color: blue; font-size: 18px;'>**Price:** $ {selected_item['price']}</span>", unsafe_allow_html=True)
                                col2.markdown(f"<span style='color: blue; font-size: 18px;'>**Available colors:** {selected_item['color1']}, {selected_item['color2']} </span>", unsafe_allow_html=True)
                                
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
