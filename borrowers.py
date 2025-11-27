"""
Borrower management for the Library Management System.
Handles creation and retrieval of borrower records.
"""

from db import get_connection, get_dict_cursor


class DuplicateBorrowerError(Exception):
    """Raised when a borrower with the same SSN already exists."""
    pass


def create_borrower(ssn: str, name: str, address: str, phone: str) -> int:
    """
    Create a new borrower in the BORROWER table.

    - All parameters must be non-empty; raise ValueError if any is invalid.
    - Enforce one borrower per SSN:
        * If a borrower with this SSN already exists, raise DuplicateBorrowerError.
    - Generate a new Card_id:
        * Card_id = (current MAX(Card_id)) + 1, or 1 if table is empty.
    - Insert the new borrower row and return the new Card_id.
    
    Args:
        ssn: Social Security Number (must be unique)
        name: Borrower's full name
        address: Borrower's address
        phone: Borrower's phone number
        
    Returns:
        int: The newly generated Card_id
        
    Raises:
        ValueError: If any parameter is empty
        DuplicateBorrowerError: If a borrower with this SSN already exists
    """
    # Validate inputs
    if not ssn or not name or not address or not phone:
        raise ValueError("All borrower fields (SSN, name, address, phone) must be non-empty")
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        # Check if SSN already exists
        cursor.execute("SELECT Card_id FROM BORROWER WHERE Ssn = %s", (ssn,))
        existing = cursor.fetchone()
        if existing:
            raise DuplicateBorrowerError(f"A borrower with SSN {ssn} already exists")
        
        # Get next Card_id
        cursor.execute("SELECT MAX(Card_id) AS max_id FROM BORROWER")
        result = cursor.fetchone()
        new_card_id = (result['max_id'] or 0) + 1
        
        # Insert new borrower
        insert_sql = """
            INSERT INTO BORROWER (Card_id, Ssn, Bname, Address, Phone)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (new_card_id, ssn, name, address, phone))
        conn.commit()
        
        return new_card_id
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_borrower_by_card(card_id: int) -> dict | None:
    """
    Return borrower row as dict for this card_id, or None if not found.
    
    Args:
        card_id: The borrower's card ID
        
    Returns:
        dict | None: Borrower record with keys matching column names, or None
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        cursor.execute("SELECT * FROM BORROWER WHERE Card_id = %s", (card_id,))
        return cursor.fetchone()
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_borrower_by_ssn(ssn: str) -> dict | None:
    """
    Return borrower row as dict for this SSN, or None if not found.
    
    Args:
        ssn: The borrower's Social Security Number
        
    Returns:
        dict | None: Borrower record with keys matching column names, or None
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        cursor.execute("SELECT * FROM BORROWER WHERE Ssn = %s", (ssn,))
        return cursor.fetchone()
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


