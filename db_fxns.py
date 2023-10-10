# DB
import csv
import os
import sqlite3
conn = sqlite3.connect('data.db',check_same_thread=False)
c = conn.cursor()

# Functions

def create_item_table():
	c.execute('CREATE TABLE IF NOT EXISTS itemstable(category TEXT,subcategory TEXT,name TEXT,price INTEGER,discount INTEGER,likes INTEGER,isnew TEXT,brand TEXT,colour1 TEXT,colour2 TEXT,photo TEXT)')

def add_item_data(category,subcategory,name,price,discount,likes,isnew,brand,colour1,colour2,photo):
	c.execute('INSERT INTO itemstable(category,subcategory,name,price,discount,likes,isnew,brand,colour1,colour2,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
		   (category,subcategory,name,price,discount,likes,isnew,brand,colour1,colour2,photo))
	conn.commit()

def view_all_inventry_items():
	c.execute('SELECT * FROM itemstable')
	data = c.fetchall()
	return data

def view_unique_item():
    c.execute('SELECT DISTINCT name FROM itemstable')
    data = c.fetchall()
    return data

def get_item(name):
    c.execute('SELECT * FROM itemstable WHERE name = "{}" '.format(name))
    data = c.fetchall()
    return data

def edit_item(newitem_category,newitem_sub_category,newitem_name,newitem_price,newitem_discount,newitem_isnew,newitem_brand,
			  newitem_color_varient_1,newitem_color_varient_2,newitem_image,get_category,get_subcategory,get_name,get_price,
			  get_discount,get_isnew,get_brand,get_colour1,get_colour2,get_url):
    c.execute('UPDATE itemstable SET category=?,subcategory=?,name=?,price=?,discount=?,likes=0,isnew=?,brand=?,colour1=?,colour2=?,photo=?  WHERE category=? AND subcategory=? and name=? AND price=? AND discount=? AND likes=0 AND isnew=? AND brand=? AND colour1=? AND colour2=? and photo=?',
			  (newitem_category,newitem_sub_category,newitem_name,newitem_price,newitem_discount,newitem_isnew,newitem_brand,
			  newitem_color_varient_1,newitem_color_varient_2,newitem_image,get_category,get_subcategory,get_name,get_price,
			  get_discount,get_isnew,get_brand,get_colour1,get_colour2,get_url))
    conn.commit()
    data = c.fetchall()
    return data

def delete_item(name):
	c.execute('DELETE FROM itemstable WHERE name="{}"'.format(name))
	conn.commit()


# Login/Signup



def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable (name TEXT, age INTEGER, gender TEXT, username TEXT PRIMARY KEY, password TEXT,usertype TEXT)')


def add_userdata(name,age,gender,username,password,usertype):
	c.execute('INSERT INTO userstable(name,age,gender,username,password,usertype) VALUES (?,?,?,?,?,?)',
		   (name,age,gender,username,password,usertype))
	conn.commit()
	

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

def get_user_type(username):
    c.execute('SELECT usertype FROM userstable WHERE username = ?', (username,))
    user_type = c.fetchone()
    if user_type:
        return user_type[0]
    else:
        return None


# Function to create Item rating table

def create_item_rating_table(): 
    cursor = conn.cursor()
    # Define the SQL command to create the item_rating table
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS item_rating (
        RatingID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        UserName TEXT,
        ItemName TEXT,
        Rating INTEGER,
        FOREIGN KEY (UserID) REFERENCES userstable (rowid),  -- Assuming userstable has a rowid column
        FOREIGN KEY (UserName) REFERENCES userstable (username) -- Assuming userstable has a username column
    );
    '''
    cursor.execute(create_table_query)
    conn.commit()

def save_item_rating(username, item_name, rating):
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    try:
        # Insert the rating into the item_rating table
        cursor.execute("INSERT INTO item_rating (UserID, UserName, ItemName, Rating) VALUES (?, ?, ?, ?)",
                       (get_user_id(username), username, item_name, rating))
        cursor.execute("SELECT UserID, UserName, ItemName, Rating FROM item_rating ORDER BY RowID DESC LIMIT 1")
        last_updated_data = cursor.fetchone()
        if last_updated_data:
            # Construct the file path
            file_path = os.path.join('data', 'rating.csv')

            # Write data to the CSV file
            if os.path.exists(file_path):
                # Read existing data from the CSV file
                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    existing_data = list(csv.reader(file))

                # Append the new data to the existing data
                existing_data.append(last_updated_data)

                # Write all data (including existing and new) back to the file
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(existing_data)
                    
        # Commit the changes
        conn.commit()
        return True  # Return True to indicate successful saving of rating
    except Exception as e:
        print(f"Error saving rating: {e}")
        conn.rollback()
        return False  # Return False to indicate an error occurred while saving rating

# Function to get the UserID based on the username
def get_user_id(username):
    c.execute('SELECT rowid FROM userstable WHERE username = ?', (username,))
    user_id = c.fetchone()
    if user_id:
        return user_id[0]
    else:
        return None
    


"""
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
"""