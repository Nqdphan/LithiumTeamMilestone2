"""
Database initialization module for the Library Management System.
Creates all necessary tables and imports initial data from CSV files.
"""

import os
import csv
from db import get_connection, get_dict_cursor


# CSV file paths (relative to this file's directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOK_CSV = os.path.join(BASE_DIR, "book.csv")
AUTHORS_CSV = os.path.join(BASE_DIR, "authors.csv")
BOOK_AUTHORS_CSV = os.path.join(BASE_DIR, "book_authors.csv")
BORROWER_CSV = os.path.join(BASE_DIR, "borrower.csv")


def create_tables(cursor):
    """
    Create all necessary tables if they do not exist.
    
    Args:
        cursor: MySQL cursor object
    """
    print("Creating tables if not exist...")
    
    # Create BOOK table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BOOK (
            Isbn  VARCHAR(20) NOT NULL,
            Title VARCHAR(255) NOT NULL,
            CONSTRAINT pk_book PRIMARY KEY (Isbn)
        )
    """)
    
    # Create AUTHORS table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AUTHORS (
            Author_id INT NOT NULL,
            Name      VARCHAR(255) NOT NULL,
            CONSTRAINT pk_authors PRIMARY KEY (Author_id)
        )
    """)
    
    # Create BORROWER table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BORROWER (
            Card_id VARCHAR(20) PRIMARY KEY,
            Ssn     VARCHAR(20) NOT NULL UNIQUE,
            Bname   VARCHAR(255) NOT NULL,
            Address VARCHAR(255) NOT NULL,
            Phone   VARCHAR(20) NOT NULL
        )
    """)
    
    # Create BOOK_AUTHORS table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BOOK_AUTHORS (
            Author_id INT NOT NULL,
            Isbn      VARCHAR(20) NOT NULL,
            CONSTRAINT pk_book_authors PRIMARY KEY (Author_id, Isbn),
            CONSTRAINT fk_book_authors_author FOREIGN KEY (Author_id)
                REFERENCES AUTHORS(Author_id),
            CONSTRAINT fk_book_authors_book FOREIGN KEY (Isbn)
                REFERENCES BOOK(Isbn)
        )
    """)
    
    # Create BOOK_LOANS table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BOOK_LOANS (
            Loan_id   INT AUTO_INCREMENT,
            Isbn      VARCHAR(20) NOT NULL,
            Card_id   VARCHAR(20) NOT NULL,
            Date_out  DATE NOT NULL,
            Due_date  DATE NOT NULL,
            Date_in   DATE,
            CONSTRAINT pk_book_loans PRIMARY KEY (Loan_id),
            CONSTRAINT fk_book_loans_book FOREIGN KEY (Isbn)
                REFERENCES BOOK(Isbn),
            CONSTRAINT fk_book_loans_borrower FOREIGN KEY (Card_id)
                REFERENCES BORROWER(Card_id)
        )
    """)
    
    # Create FINES table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FINES (
            Loan_id   INT NOT NULL,
            Fine_amt  DECIMAL(10,2) NOT NULL,
            Paid      BOOLEAN NOT NULL DEFAULT 0,
            CONSTRAINT pk_fines PRIMARY KEY (Loan_id),
            CONSTRAINT fk_fines_loan FOREIGN KEY (Loan_id)
                REFERENCES BOOK_LOANS(Loan_id)
                ON DELETE CASCADE
        )
    """)
    
    print("✓ Tables created successfully.")


def table_has_rows(cursor, table_name: str) -> bool:
    """
    Check if a table has any rows.
    
    Args:
        cursor: MySQL cursor object
        table_name: Name of the table to check
        
    Returns:
        bool: True if table has rows, False otherwise
    """
    cursor.execute(f"SELECT COUNT(*) AS c FROM {table_name}")
    result = cursor.fetchone()
    return result["c"] > 0


def import_books(cursor, path: str):
    """
    Import books from CSV file into BOOK table.
    
    Args:
        cursor: MySQL cursor object
        path: Path to book.csv file
    """
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Skipping BOOK import.")
        return
    
    print(f"Reading {path}...")
    rows_inserted = 0
    
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = []
        
        for row in reader:
            rows.append((row['Isbn'], row['Title']))
        
        if rows:
            insert_sql = "INSERT INTO BOOK (Isbn, Title) VALUES (%s, %s)"
            cursor.executemany(insert_sql, rows)
            rows_inserted = len(rows)
    
    print(f"✓ Imported {rows_inserted} rows into BOOK.")


def import_authors(cursor, path: str):
    """
    Import authors from CSV file into AUTHORS table.
    
    Args:
        cursor: MySQL cursor object
        path: Path to authors.csv file
    """
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Skipping AUTHORS import.")
        return
    
    print(f"Reading {path}...")
    rows_inserted = 0
    
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = []
        
        for row in reader:
            rows.append((int(row['Author_id']), row['Name']))
        
        if rows:
            insert_sql = "INSERT INTO AUTHORS (Author_id, Name) VALUES (%s, %s)"
            cursor.executemany(insert_sql, rows)
            rows_inserted = len(rows)
    
    print(f"✓ Imported {rows_inserted} rows into AUTHORS.")


def import_book_authors(cursor, path: str):
    """
    Import book-author relationships from CSV file into BOOK_AUTHORS table.
    
    Args:
        cursor: MySQL cursor object
        path: Path to book_authors.csv file
    """
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Skipping BOOK_AUTHORS import.")
        return
    
    print(f"Reading {path}...")
    rows_inserted = 0
    
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = []
        
        for row in reader:
            rows.append((int(row['Author_id']), row['Isbn']))
        
        if rows:
            insert_sql = "INSERT INTO BOOK_AUTHORS (Author_id, Isbn) VALUES (%s, %s)"
            cursor.executemany(insert_sql, rows)
            rows_inserted = len(rows)
    
    print(f"✓ Imported {rows_inserted} rows into BOOK_AUTHORS.")


def import_borrowers(cursor, path: str):
    """
    Import borrowers from CSV file into BORROWER table.
    
    Args:
        cursor: MySQL cursor object
        path: Path to borrower.csv file
    """
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Skipping BORROWER import.")
        return
    
    print(f"Reading {path}...")
    rows_inserted = 0
    
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = []
        
        for row in reader:
            rows.append((
                row['Card_id'],
                row['Ssn'],
                row['Bname'],
                row['Address'],
                row['Phone']
            ))
        
        if rows:
            insert_sql = """
                INSERT INTO BORROWER (Card_id, Ssn, Bname, Address, Phone)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_sql, rows)
            rows_inserted = len(rows)
    
    print(f"✓ Imported {rows_inserted} rows into BORROWER.")


def init_db():
    """
    Main initialization function.
    Creates all tables and imports data from CSV files if tables are empty.
    """
    conn = None
    cursor = None
    
    try:
        print("\n" + "=" * 60)
        print("Initializing Library Management System Database")
        print("=" * 60)
        
        # Get database connection
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        # Create all tables
        create_tables(cursor)
        
        # Import data from CSVs only if tables are empty
        print("\nChecking for existing data...")
        
        # Import BOOK
        if not table_has_rows(cursor, "BOOK"):
            print("\nBOOK table is empty. Importing from CSV...")
            import_books(cursor, BOOK_CSV)
        else:
            print("BOOK already has data, skipping import.")
        
        # Import AUTHORS
        if not table_has_rows(cursor, "AUTHORS"):
            print("\nAUTHORS table is empty. Importing from CSV...")
            import_authors(cursor, AUTHORS_CSV)
        else:
            print("AUTHORS already has data, skipping import.")
        
        # Import BORROWER
        if not table_has_rows(cursor, "BORROWER"):
            print("\nBORROWER table is empty. Importing from CSV...")
            import_borrowers(cursor, BORROWER_CSV)
        else:
            print("BORROWER already has data, skipping import.")
        
        # Import BOOK_AUTHORS (must be imported after BOOK and AUTHORS)
        if not table_has_rows(cursor, "BOOK_AUTHORS"):
            print("\nBOOK_AUTHORS table is empty. Importing from CSV...")
            import_book_authors(cursor, BOOK_AUTHORS_CSV)
        else:
            print("BOOK_AUTHORS already has data, skipping import.")
        
        # Commit all changes
        conn.commit()
        print("\n" + "=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n✗ Error during database initialization: {e}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



