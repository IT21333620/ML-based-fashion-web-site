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
                             st.write("This is marketplace")


                        elif task == "Cart":
                             st.write("This is cart")


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
                            suggestion_type = st.radio("Select Suggestion type",["Item Base","User Base"])

                            if suggestion_type == "Item Base":
                                st.write("Item based")
                                orderitem = view_cart()
                                if orderitem:
                                    selectItem = st.selectbox("Match to", orderitem)
                                else:
                                    st.write("No items in the cart.") 


                            elif suggestion_type == "User Base":
                                st.write("User based")
                            else:
                                st.write("Error.")



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
                             st.write("Add Desired Item")


                        elif task == "View Added Item":
                             st.write("View added item")


                        elif task == "Update Item":
                             st.write("Update items")


                        elif task == "Delete Item":
                             st.write("Delete items")


                        elif task == "Forcasts":
                             st.write("View sales forcasts")
                             

                    else:
                        st.error("Unknown user type")
                else:
                    st.error("Failed to retrieve user type")
            else:
                st.error("Login failed. Please check your credentials.")

        

if __name__ == '__main__':
    main()
