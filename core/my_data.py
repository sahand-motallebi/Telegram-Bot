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
def add_user(conn, first_name, last_name, hire_date):
    cursorObj = conn.cursor()
    cursorObj.execute("INSERT INTO members (first_name, last_name, hiredate) VALUES (?, ?, ?)", (first_name, last_name, hire_date))
    conn.commit()

def close_connection(conn):
    if conn:
        conn.close()