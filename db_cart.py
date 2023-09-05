# DB
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