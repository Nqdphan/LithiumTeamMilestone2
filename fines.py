"""
Fine management for the Library Management System.
Handles fine calculation, updates, and payment processing.
"""

from datetime import date
from db import get_connection, get_dict_cursor


class BooksStillOutError(Exception):
    """Raised when trying to pay fines but some loans are still not returned."""
    pass


def update_fines(today: date | None = None) -> None:
    """
    Recompute fines for all overdue loans based on current dates.

    Fine rules:
      - Rate: $0.25 per late day.
      - Returned late:
          if Date_in > Due_date:
              late_days = DATEDIFF(Date_in, Due_date)
      - Still checked out & overdue:
          if Date_in IS NULL and today > Due_date:
              late_days = DATEDIFF(today, Due_date)

    For each Loan_id with late_days > 0:
      - Fine_amt = late_days * 0.25 (DECIMAL(10,2)).
      - If no FINES row exists yet, INSERT with Paid = 0.
      - If FINES row exists and Paid = 0, UPDATE Fine_amt if it changed.
      - If Paid = 1, leave it unchanged.

    Use minimal number of queries and transactions for efficiency.
    
    Args:
        today: The date to use for calculating current fines (defaults to today)
    """
    if today is None:
        today = date.today()
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        # Find all overdue loans and calculate their fines
        calculate_fines_sql = """
            SELECT 
                bl.Loan_id,
                CASE
                    WHEN bl.Date_in IS NOT NULL AND bl.Date_in > bl.Due_date THEN
                        DATEDIFF(bl.Date_in, bl.Due_date)
                    WHEN bl.Date_in IS NULL AND %s > bl.Due_date THEN
                        DATEDIFF(%s, bl.Due_date)
                    ELSE 0
                END AS late_days
            FROM BOOK_LOANS bl
            HAVING late_days > 0
        """
        
        cursor.execute(calculate_fines_sql, (today, today))
        overdue_loans = cursor.fetchall()
        
        for loan in overdue_loans:
            loan_id = loan['Loan_id']
            fine_amt = loan['late_days'] * 0.25
            
            # Check if fine exists
            cursor.execute("SELECT Paid FROM FINES WHERE Loan_id = %s", (loan_id,))
            existing_fine = cursor.fetchone()
            
            if existing_fine is None:
                # Insert new fine
                cursor.execute(
                    "INSERT INTO FINES (Loan_id, Fine_amt, Paid) VALUES (%s, %s, 0)",
                    (loan_id, fine_amt)
                )
            elif existing_fine['Paid'] == 0:
                # Update unpaid fine
                cursor.execute(
                    "UPDATE FINES SET Fine_amt = %s WHERE Loan_id = %s",
                    (fine_amt, loan_id)
                )
            # If Paid = 1, do nothing
        
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


def get_fines_summary(card_id: int | None = None,
                      include_paid: bool = False) -> list[dict]:
    """
    Return per-borrower fine summaries.

    - Join BORROWER, BOOK_LOANS, and FINES.
    - If card_id is provided, restrict to that borrower.
    - If include_paid is False, ignore rows where Paid = 1.
    - Group by Card_id.

    Each result dict should contain:
      - 'card_id'
      - 'borrower_name'
      - 'total_fine' (sum of Fine_amt for that borrower)
      
    Args:
        card_id: Optional card ID to filter by specific borrower
        include_paid: Whether to include paid fines in the summary
        
    Returns:
        list[dict]: List of fine summaries per borrower
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        sql = """
            SELECT 
                br.Card_id AS card_id,
                br.Bname AS borrower_name,
                SUM(f.Fine_amt) AS total_fine
            FROM BORROWER br
            INNER JOIN BOOK_LOANS bl ON br.Card_id = bl.Card_id
            INNER JOIN FINES f ON bl.Loan_id = f.Loan_id
            WHERE 1=1
        """
        
        params = []
        
        if not include_paid:
            sql += " AND f.Paid = 0"
        
        if card_id is not None:
            sql += " AND br.Card_id = %s"
            params.append(card_id)
        
        sql += " GROUP BY br.Card_id, br.Bname ORDER BY br.Bname"
        
        cursor.execute(sql, params)
        return cursor.fetchall()
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def pay_all_fines(card_id: int) -> None:
    """
    Pay all unpaid fines for a borrower.

    Rules:
      - Fines can only be paid for loans that have been returned
        (BOOK_LOANS.Date_in IS NOT NULL).
      - If there exists any unpaid fine (Paid = 0) for this borrower
        where the corresponding loan has Date_in IS NULL,
        raise BooksStillOutError and do not update anything.
      - Otherwise, set Paid = 1 for all FINES rows for this borrower
        where Paid = 0.

    Use a transaction and commit/rollback appropriately.
    
    Args:
        card_id: The borrower's card ID
        
    Raises:
        BooksStillOutError: If borrower has unpaid fines for unreturned books
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        # Check for unpaid fines on books still checked out
        check_sql = """
            SELECT COUNT(*) AS cnt
            FROM BOOK_LOANS bl
            INNER JOIN FINES f ON bl.Loan_id = f.Loan_id
            WHERE bl.Card_id = %s
            AND f.Paid = 0
            AND bl.Date_in IS NULL
        """
        cursor.execute(check_sql, (card_id,))
        if cursor.fetchone()['cnt'] > 0:
            raise BooksStillOutError(
                f"Cannot pay fines for borrower {card_id}: some books with fines are still checked out"
            )
        
        # Pay all unpaid fines for returned books
        pay_sql = """
            UPDATE FINES f
            INNER JOIN BOOK_LOANS bl ON f.Loan_id = bl.Loan_id
            SET f.Paid = 1
            WHERE bl.Card_id = %s
            AND f.Paid = 0
            AND bl.Date_in IS NOT NULL
        """
        cursor.execute(pay_sql, (card_id,))
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


