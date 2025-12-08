"""
Loans router for the Library Management System API.
Handles book checkout and check-in operations.
"""

from datetime import date, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from db import get_connection, get_dict_cursor

router = APIRouter()


class CheckoutRequest(BaseModel):
    isbn: str = Field(..., description="ISBN of the book to checkout")
    card_id: str = Field(..., description="Borrower's card ID")


class CheckinRequest(BaseModel):
    loan_id: int = Field(..., description="Loan ID to check in")


@router.post("/checkout")
def checkout_book(request: CheckoutRequest):
    """
    Checkout a book to a borrower.
    
    Business rules:
    - Book must not be currently checked out
    - Borrower must have fewer than 3 active loans
    - Borrower must not have unpaid fines
    
    Returns the new Loan_id on success.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        # Verify borrower exists
        cursor.execute("SELECT Card_id FROM BORROWER WHERE Card_id = %s", (request.card_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Borrower with Card ID {request.card_id} not found")
        
        # Check for unpaid fines
        unpaid_fines_sql = """
            SELECT COUNT(*) AS cnt
            FROM BOOK_LOANS bl
            INNER JOIN FINES f ON bl.Loan_id = f.Loan_id
            WHERE bl.Card_id = %s AND f.Paid = 0
        """
        cursor.execute(unpaid_fines_sql, (request.card_id,))
        if cursor.fetchone()['cnt'] > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Borrower {request.card_id} has unpaid fines"
            )
        
        # Check active loan count
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM BOOK_LOANS WHERE Card_id = %s AND Date_in IS NULL",
            (request.card_id,)
        )
        active_count = cursor.fetchone()['cnt']
        if active_count >= 3:
            raise HTTPException(
                status_code=400,
                detail=f"Borrower {request.card_id} already has {active_count} active loans (maximum is 3)"
            )
        
        # Check if book is available
        cursor.execute(
            "SELECT Loan_id FROM BOOK_LOANS WHERE Isbn = %s AND Date_in IS NULL",
            (request.isbn,)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"Book {request.isbn} is already checked out"
            )
        
        # Verify book exists
        cursor.execute("SELECT Isbn FROM BOOK WHERE Isbn = %s", (request.isbn,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Book with ISBN {request.isbn} not found")
        
        # Create the loan
        today = date.today()
        due_date = today + timedelta(days=14)
        insert_sql = """
            INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in)
            VALUES (%s, %s, %s, %s, NULL)
        """
        cursor.execute(insert_sql, (request.isbn, request.card_id, today, due_date))
        loan_id = cursor.lastrowid
        conn.commit()
        
        return {
            "loan_id": loan_id,
            "isbn": request.isbn,
            "card_id": request.card_id,
            "date_out": today.isoformat(),
            "due_date": due_date.isoformat(),
            "message": "Book checked out successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error during checkout: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/open")
def get_open_loans(
    isbn: Optional[str] = None,
    card_id: Optional[str] = None,
    name_query: Optional[str] = None
):
    """
    Get all open (not yet checked-in) loans.
    
    Optional filters:
    - isbn: Filter by exact ISBN
    - card_id: Filter by exact card ID
    - name_query: Filter by borrower name substring
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
        results = cursor.fetchall()
        
        # Convert date objects to strings
        for row in results:
            if row['date_out']:
                row['date_out'] = row['date_out'].isoformat() if isinstance(row['date_out'], date) else str(row['date_out'])
            if row['due_date']:
                row['due_date'] = row['due_date'].isoformat() if isinstance(row['due_date'], date) else str(row['due_date'])
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching open loans: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/checkin")
def checkin_book(request: CheckinRequest):
    """
    Check in a book by loan ID.
    
    Sets Date_in to today for the specified loan.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        # Verify loan exists and is not already checked in
        cursor.execute(
            "SELECT Loan_id FROM BOOK_LOANS WHERE Loan_id = %s AND Date_in IS NULL",
            (request.loan_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Loan {request.loan_id} not found or already checked in"
            )
        
        # Update loan
        today = date.today()
        update_sql = """
            UPDATE BOOK_LOANS
            SET Date_in = %s
            WHERE Loan_id = %s
            AND Date_in IS NULL
        """
        cursor.execute(update_sql, (today, request.loan_id))
        conn.commit()
        
        return {
            "loan_id": request.loan_id,
            "date_in": today.isoformat(),
            "message": "Book checked in successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error during check-in: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



