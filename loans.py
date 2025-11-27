"""
Loan management for the Library Management System.
Handles book checkout, check-in, and loan searches.
"""

from datetime import date, timedelta
from db import get_connection, get_dict_cursor


class MaxLoansError(Exception):
    """Borrower already has the maximum number of active loans."""
    pass


class BookNotAvailableError(Exception):
    """Book is already checked out (no available copy)."""
    pass


class UnpaidFinesError(Exception):
    """Borrower has unpaid fines and cannot check out more books."""
    pass


def checkout_book(isbn: str, card_id: int, today: date | None = None) -> int:
    """
    Checkout a book to a borrower.

    Business rules:
      - Borrower may have at most 3 active loans (Date_in IS NULL).
        If they already have 3, raise MaxLoansError.
      - The book must not already be checked out:
        if any BOOK_LOANS row exists for this ISBN with Date_in IS NULL,
        raise BookNotAvailableError.
      - Borrower must not have any unpaid fines:
        join BOOK_LOANS -> FINES where Paid = 0 for this Card_id.
        If any exist, raise UnpaidFinesError.

    On success:
      - Use 'today' as Date_out (default date.today()).
      - Due_date = today + 14 days.
      - Insert a row into BOOK_LOANS with Date_in = NULL.
      - Return the new Loan_id (cursor.lastrowid).
      
    Args:
        isbn: The ISBN of the book to checkout
        card_id: The borrower's card ID
        today: The checkout date (defaults to today)
        
    Returns:
        int: The new Loan_id
        
    Raises:
        MaxLoansError: If borrower has 3 active loans
        BookNotAvailableError: If book is already checked out
        UnpaidFinesError: If borrower has unpaid fines
    """
    if today is None:
        today = date.today()
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        # Check for unpaid fines
        unpaid_fines_sql = """
            SELECT COUNT(*) AS cnt
            FROM BOOK_LOANS bl
            INNER JOIN FINES f ON bl.Loan_id = f.Loan_id
            WHERE bl.Card_id = %s AND f.Paid = 0
        """
        cursor.execute(unpaid_fines_sql, (card_id,))
        if cursor.fetchone()['cnt'] > 0:
            raise UnpaidFinesError(f"Borrower {card_id} has unpaid fines")
        
        # Check active loan count
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM BOOK_LOANS WHERE Card_id = %s AND Date_in IS NULL",
            (card_id,)
        )
        active_count = cursor.fetchone()['cnt']
        if active_count >= 3:
            raise MaxLoansError(f"Borrower {card_id} already has {active_count} active loans")
        
        # Check if book is available
        cursor.execute(
            "SELECT Loan_id FROM BOOK_LOANS WHERE Isbn = %s AND Date_in IS NULL",
            (isbn,)
        )
        if cursor.fetchone():
            raise BookNotAvailableError(f"Book {isbn} is already checked out")
        
        # Create the loan
        due_date = today + timedelta(days=14)
        insert_sql = """
            INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in)
            VALUES (%s, %s, %s, %s, NULL)
        """
        cursor.execute(insert_sql, (isbn, card_id, today, due_date))
        conn.commit()
        
        return cursor.lastrowid
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def find_active_loans(isbn: str | None = None,
                      card_id: int | None = None,
                      name_query: str | None = None) -> list[dict]:
    """
    Search active (not yet checked-in) loans.

    Filters:
      - Only loans where Date_in IS NULL.
      - Optional exact ISBN filter.
      - Optional exact Card_id filter.
      - Optional case-insensitive substring search on BORROWER.Bname.

    Return list of dicts with:
      - 'loan_id'
      - 'isbn'
      - 'title'
      - 'card_id'
      - 'borrower_name'
      - 'date_out'
      - 'due_date'
      
    Args:
        isbn: Optional exact ISBN to filter by
        card_id: Optional exact card ID to filter by
        name_query: Optional substring to search in borrower name
        
    Returns:
        list[dict]: List of active loans matching the criteria
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        sql = """
            SELECT 
                bl.Loan_id AS loan_id,
                bl.Isbn AS isbn,
                b.Title AS title,
                bl.Card_id AS card_id,
                br.Bname AS borrower_name,
                bl.Date_out AS date_out,
                bl.Due_date AS due_date
            FROM BOOK_LOANS bl
            INNER JOIN BOOK b ON bl.Isbn = b.Isbn
            INNER JOIN BORROWER br ON bl.Card_id = br.Card_id
            WHERE bl.Date_in IS NULL
        """
        
        params = []
        
        if isbn is not None:
            sql += " AND bl.Isbn = %s"
            params.append(isbn)
        
        if card_id is not None:
            sql += " AND bl.Card_id = %s"
            params.append(card_id)
        
        if name_query is not None:
            sql += " AND LOWER(br.Bname) LIKE %s"
            params.append(f"%{name_query.lower()}%")
        
        sql += " ORDER BY bl.Due_date"
        
        cursor.execute(sql, params)
        return cursor.fetchall()
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def checkin_loans(loan_ids: list[int], today: date | None = None) -> None:
    """
    Check in one or more loans.

    - Default 'today' to date.today().
    - For each loan_id, if Date_in IS NULL, set Date_in = today.
    - Use a single transaction to update all specified loan_ids.
    - Ignore non-existent loan_ids gracefully.
    
    Args:
        loan_ids: List of loan IDs to check in
        today: The check-in date (defaults to today)
    """
    if not loan_ids:
        return
    
    if today is None:
        today = date.today()
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build placeholders for the IN clause
        placeholders = ', '.join(['%s'] * len(loan_ids))
        update_sql = f"""
            UPDATE BOOK_LOANS
            SET Date_in = %s
            WHERE Loan_id IN ({placeholders})
            AND Date_in IS NULL
        """
        
        cursor.execute(update_sql, [today] + loan_ids)
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

