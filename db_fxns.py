# DB
import sqlite3
conn = sqlite3.connect('data.db',check_same_thread=False)
c = conn.cursor()

# Functions

def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT,title TEXT,article TEXT,postdate DATE)')

def add_data(author,title,article,postdate):
	c.execute('INSERT INTO blogtable(author,title,article,postdate) VALUES (?,?,?,?)',(author,title,article,postdate))
	conn.commit()

def view_all_notes():
	c.execute('SELECT * FROM blogtable')
	data = c.fetchall()
	return data

def view_all_titles():
	c.execute('SELECT DISTINCT title FROM blogtable')
	data = c.fetchall()
	return data


def get_blog_by_title(title):
	c.execute('SELECT * FROM blogtable WHERE title="{}"'.format(title))
	data = c.fetchall()
	return data

def get_blog_by_author(author):
	c.execute('SELECT * FROM blogtable WHERE author="{}"'.format(author))
	data = c.fetchall()
	return data


def delete_data(title):
	c.execute('DELETE FROM blogtable WHERE title="{}"'.format(title))
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
