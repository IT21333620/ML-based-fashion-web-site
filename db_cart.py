# DB
import csv
import os
import sqlite3
conn = sqlite3.connect('cart.db',check_same_thread=False)
c = conn.cursor()

# Functions
def create_cart_table():
    c.execute('''CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT, category TEXT, item_name TEXT, price REAL, total_price REAL, quantity INTEGER)''')
    conn.commit()

def add_item_cart(user_name, category, item_name, price, total_price, quantity):
    c.execute("INSERT INTO cart (user_name, category, item_name, price, total_price, quantity) VALUES (?, ?, ?, ?, ?, ?)", (user_name, category, item_name, price, total_price, quantity))
    conn.commit()

def delete_cart(username):
    """
    Delete all items in the cart for a specific user.
    """
    c.execute("DELETE FROM cart WHERE user_name=?", (username,))
    conn.commit()


def view_all_items(username):
    """
    Retrieve all items in the cart for a specific user.
    """
    c.execute("SELECT user_name, item_name, category, total_price, quantity FROM cart WHERE user_name=?", (username,))
    items = c.fetchall()
    return items

def view_cart_item(username):
    c.execute("SELECT item_name From cart where user_name=?",(username,))
    data = c.fetchall()
    return  [item[0] for item in data]

def viewCatogory(name):
    c.execute("Select category from cart where item_name=?",(name,))
    data = c.fetchall()
    return data

# Perchase History

def make_purchase(username):
    # Retrieve items from the cart for the user
    cart_items = view_cart(username)
    if cart_items:
        # Create a purchase history table if it doesn't exist
        create_purchase_history_table()
        # Loop through cart items and save them to the purchase history
        for item in cart_items:
            # Check the length of the item tuple before unpacking
            if len(item) >= 6:
                user_name, item_name,category, price,total_price, quantity = item
                # Insert the purchased item into the purchase history table
                c.execute("INSERT INTO purchase_history (user_name, item_name,category,price, total_price, quantity) VALUES (?, ?, ?, ?, ?,?)", (user_name, item_name,category, price,total_price, quantity))
                conn.commit()
                # Clear the user's cart after the purchase
                delete_cart(username)
        return True
    else:
        return False

def view_cart(username):
    c.execute("SELECT user_name, item_name, category,price, total_price, quantity FROM cart WHERE user_name=?", (username,))
    items = c.fetchall()
    return items

def delete_item_from_cart(username, item_name):
    """
    Delete a specific item from the cart for a specific user.
    """
    c.execute("DELETE FROM cart WHERE user_name=? AND item_name=?", (username, item_name))
    conn.commit()

def update_cart_quantities(username, cart_df):
    conn = sqlite3.connect('cart.db')
    cursor = conn.cursor()

    for index, row in cart_df.iterrows():
        item_name = row['Item Name']
        new_quantity = row['Quantity']
        new_total_price = row['Total Price'] * new_quantity  # Calculate new total price
        
        # Update the quantity and total price in the database
        cursor.execute("UPDATE cart SET quantity = ?, total_price = ? WHERE user_name = ? AND item_name = ?", 
                       (new_quantity, new_total_price, username, item_name))

    conn.commit()
    conn.close()
    return new_total_price

def calculate_cart_subtotal(username):
    conn = sqlite3.connect("cart.db")
    c = conn.cursor()
    c.execute("SELECT SUM(total_price) FROM cart WHERE user_name=?", (username,))
    subtotal = c.fetchone()[0]
    conn.close()
    return subtotal

def create_payment_details_table():
    conn = sqlite3.connect('cart.db')  # Connect to your database
    c = conn.cursor()

    c.execute('''
              CREATE TABLE IF NOT EXISTS payment_details
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               account_number TEXT,
               expiration_month INTEGER,
               expiration_year INTEGER,
               cvv INTEGER,
               purchase_date DATE)
              ''')

    conn.commit()

def add_payment_details(account_number, expiration_month, expiration_year, cvv, purchase_date):
    conn = sqlite3.connect('cart.db')  # Connect to your database
    c = conn.cursor()
    create_payment_details_table()

    c.execute('''
    INSERT INTO payment_details
    (account_number, expiration_month, expiration_year, cvv, purchase_date)
    VALUES (?, ?, ?, ?, ?)
    ''', (account_number, expiration_month, expiration_year, cvv, purchase_date))

    conn.commit()

# Define a function to create the purchase history table
def create_purchase_history_table():
    conn = sqlite3.connect('cart.db')  
    c = conn.cursor()
    # Define the SQL query to create the purchase history table
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS purchase_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        category TEXT NOT NULL,
        item_name TEXT NOT NULL,
        price REAL NOT NULL,
        total_price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    # Execute the SQL query to create the table
    c.execute(create_table_query)
    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

def view_purchase_history(username):
    conn = sqlite3.connect('cart.db')
    c = conn.cursor()
    # Query to retrieve purchase history for a specific user
    c.execute('''CREATE TABLE IF NOT EXISTS purchase_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                category TEXT NOT NULL,
                item_name TEXT NOT NULL,
                price REAL NOT NULL,
                total_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
             )''')
    c.execute("SELECT * FROM purchase_history WHERE user_name = ?", (username,))
    purchase_history = c.fetchall()
    # Close the database connection
    conn.close()
    return purchase_history

def delete_purchase_hisory(username):
    """
    Delete all items in the purchase_hisory for a specific user.
    """
    c.execute("DELETE FROM purchase_history WHERE user_name=?", (username,))
def create_payment_details_table():
    conn = sqlite3.connect('cart.db')  # Connect to your database
    c = conn.cursor()

    c.execute('''
              CREATE TABLE IF NOT EXISTS payment_details
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               account_number TEXT,
               expiration_month INTEGER,
               expiration_year INTEGER,
               cvv INTEGER,
               purchase_date DATE)
              ''')

    conn.commit()

def export_to_csv():
    conn = sqlite3.connect('cart.db')
    c = conn.cursor()

    c.execute('SELECT * FROM purchase_history')
    data = c.fetchall()

    file_path = os.path.join('data', 'payment_history.csv')

    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'user_name', 'category', 'item_name', 'price', 'total_price','quantity','purchase_date'])
        writer.writerows(data)

    conn.close()

def add_payment_details(account_number, expiration_month, expiration_year, cvv, purchase_date):
    conn = sqlite3.connect('cart.db')  # Connect to your database
    c = conn.cursor()
    create_payment_details_table()

    c.execute('''
    INSERT INTO payment_details
    (account_number, expiration_month, expiration_year, cvv, purchase_date)
    VALUES (?, ?, ?, ?, ?)
    ''', (account_number, expiration_month, expiration_year, cvv, purchase_date))

    conn.commit()

#Inventory functions
def is_cart_empty(username):
    c.execute("SELECT COUNT(*) FROM cart WHERE user_name = ?", (username,))
    count = c.fetchone()[0]
    return count == 0

def get_cart_items(username):
    c.execute("SELECT item_name, quantity FROM cart WHERE user_name=?", (username,))
    cart_items = c.fetchall()
    return cart_items

def remove_item_from_cart(username, item_name):
    c.execute("DELETE FROM cart WHERE user_name = ? AND item_name = ?", (username, item_name))

#Order functions
def create_order_table():
    c.execute('''CREATE TABLE IF NOT EXISTS ordertable (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, item_quantity INTEGER)''')

def add_item_order(item_name, item_quantity):
    c.execute("INSERT INTO ordertable (item_name, item_quantity) VALUES (?, ?)", (item_name, item_quantity))
    conn.commit()

def delete_order():
    c.execute("DELETE FROM ordertable")
    conn.commit()

def delete_received_order(selected_item):
    c.execute('DELETE FROM ordertable WHERE item_name=?', (selected_item,))
    conn.commit()

def get_order_quantity(selected_item):
    c.execute('SELECT item_quantity FROM ordertable WHERE item_name=?', (selected_item,))
    quantity = c.fetchone()
    return quantity

def get_unique_order():
    c.execute('SELECT DISTINCT item_name FROM ordertable')
    item_names = [row[0] for row in c.fetchall()]
    return item_names