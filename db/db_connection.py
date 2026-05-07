import os
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager
import streamlit as st
import atexit

load_dotenv()

# Global connection variable
conn = None

@st.cache_resource
def create_connection():
    """
        Create database connection only once.
        If connection already exists and is active,
        reuse it.
    """
    global conn

    if conn is None or conn.closed:
        conn = psycopg2.connect(
            host=os.getenv("HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD_DB"),
            port=os.getenv("PORT")
        )
        print("✅Database connected successfully...")

        # Register cleanup when python process ends
        atexit.register(close_connection)

    return conn

def close_connection():
    """
        Close database connection when
        program finishes.
    """
    global conn

    if conn is not None and not conn.closed:
        conn.close()
        print("✅ Database connection closed successfully...")



@contextmanager
def get_cursor():
    """
    Create cursor for query execution.

    - Opens connection if needed
    - Creates cursor
    - Commits if success
    - Rollback if error
    - Closes cursor always
    """

    cursor = None
    connection = create_connection()

    try:
        cursor = connection.cursor()
        print("✅ Cursor object created successfully...")

        yield cursor

        connection.commit()

    except Exception:
        connection.rollback()
        print("❌ Transaction rolled back due to error...")
        raise

    finally:
        if cursor is not None:
            cursor.close()
            print("✅ Cursor object Closed successfully...")



# Explore below:
# 1) contextlib , 2) contextmanager, 3) generator for cursor, how above code is actually working.
