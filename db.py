"""
Database connection utilities for the Library Management System.
Provides connection management and cursor creation for MySQL operations.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_connection():
    """
    Create and return a new MySQL connection to the 'library' database.
    Connection parameters are read from environment variables.
    Caller is responsible for closing the connection.
    
    Required environment variables:
        DB_HOST: Database host (default: localhost)
        DB_USER: Database user (default: root)
        DB_PASSWORD: Database password (required)
        DB_NAME: Database name (default: library)
    
    Returns:
        mysql.connector.connection.MySQLConnection: Active database connection
        
    Raises:
        mysql.connector.Error: If connection cannot be established
        ValueError: If required environment variables are not set
    """
    # Get database credentials from environment variables
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "library")
    
    # Validate that password is set
    if not db_password:
        raise ValueError(
            "DB_PASSWORD environment variable is not set. "
            "Please create a .env file with your database credentials."
        )
    
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )


def get_dict_cursor(conn):
    """
    Return a cursor with dictionary=True for the given connection.
    
    Args:
        conn: MySQL connection object
        
    Returns:
        mysql.connector.cursor.MySQLCursor: Cursor that returns results as dictionaries
    """
    return conn.cursor(dictionary=True)


