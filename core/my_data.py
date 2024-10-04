import sqlite3
from sqlite3 import Error

# تابع اتصال به دیتابیس
def connection():
    try:
        conn = sqlite3.connect('my_data.db')
        return conn 
    except Error as e:
        print(e)

# تابع ایجاد جدول
def sql_table(conn):
    cursorObj = conn.cursor()
    cursorObj.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            hiredate TEXT
        )
    """)
    conn.commit()
    

# تابع برای اضافه کردن کاربر به جدول
def add_user(conn, user_id, first_name, last_name, hire_date):
    cursorObj = conn.cursor()
    cursorObj.execute("INSERT INTO members (id,first_name, last_name, hiredate) VALUES (?, ?, ?, ?)", (user_id, first_name, last_name, hire_date))
    conn.commit()
    
    
def user_exists(conn, user_id):
    cursorObj = conn.cursor()
    cursorObj.execute("SELECT * FROM members WHERE id = ?", (user_id,))
    row = cursorObj.fetchone()
    return row is not None    

def close_connection(conn):
    if conn:
        conn.close()