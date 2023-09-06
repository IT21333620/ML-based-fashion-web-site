# DB
import sqlite3
conn = sqlite3.connect('cart.db',check_same_thread=False)
c = conn.cursor()

# Functions
def create_cart_table():
    c.execute('''CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, price REAL, quantity INTEGER)''')
    conn.commit()

def add_item_cart(item_name, price, quantity):
    c.execute("INSERT INTO cart (item_name, price, quantity) VALUES (?, ?, ?)", (item_name, price, quantity))
    conn.commit()

def view_cart():
    c.execute("Select item_name FROM cart ")
    items = c.fetchall()
    return items