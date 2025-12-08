"""
Fines router for the Library Management System API.
Handles fine calculation, updates, and payment processing.
"""

from datetime import date
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from db import get_connection, get_dict_cursor

router = APIRouter()


class PayFinesRequest(BaseModel):
    card_id: str = Field(..., description="Borrower's card ID")


@router.post("/update")
def update_fines():
    """
    Recompute fines for all overdue loans.
    
    Fine rules:
    - Rate: $0.25 per late day
    - Returned late: days = (date_in - due_date)
    - Still out and overdue: days = (TODAY - due_date)
    - Only updates unpaid fines (Paid = FALSE)
    """
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
        
        updated_count = 0
        inserted_count = 0
        
        for loan in overdue_loans:
            loan_id = loan['Loan_id']
            fine_amt = float(loan['late_days']) * 0.25
            
            # Check if fine exists
            cursor.execute("SELECT Paid FROM FINES WHERE Loan_id = %s", (loan_id,))
            existing_fine = cursor.fetchone()
            
            if existing_fine is None:
                # Insert new fine
                cursor.execute(
                    "INSERT INTO FINES (Loan_id, Fine_amt, Paid) VALUES (%s, %s, 0)",
                    (loan_id, fine_amt)
                )
                inserted_count += 1
            elif existing_fine['Paid'] == 0:
                # Update unpaid fine
                cursor.execute(
                    "UPDATE FINES SET Fine_amt = %s WHERE Loan_id = %s",
                    (fine_amt, loan_id)
                )
                updated_count += 1
            # If Paid = 1, do nothing
        
        conn.commit()
        
        return {
            "message": "Fines updated successfully",
            "inserted": inserted_count,
            "updated": updated_count,
            "total_processed": len(overdue_loans)
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating fines: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/summary")
def get_fines_summary(
    unpaid_only: bool = Query(True, description="Only show unpaid fines"),
    card_id: Optional[str] = Query(None, description="Filter by specific borrower card ID")
):
    """
    Get fine summaries grouped by borrower.
    
    Returns:
    - card_id: Borrower's card ID
    - borrower_name: Borrower's name
    - total_fine_amt: Total fine amount
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
                SUM(f.Fine_amt) AS total_fine_amt
            FROM BORROWER br
            INNER JOIN BOOK_LOANS bl ON br.Card_id = bl.Card_id
            INNER JOIN FINES f ON bl.Loan_id = f.Loan_id
            WHERE 1=1
        """
        
        params = []
        
        if unpaid_only:
            sql += " AND f.Paid = 0"
        
        if card_id is not None:
            sql += " AND br.Card_id = %s"
            params.append(card_id)
        
        sql += " GROUP BY br.Card_id, br.Bname ORDER BY br.Bname"
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # Convert Decimal to float for JSON serialization
        for row in results:
            if row['total_fine_amt']:
                row['total_fine_amt'] = float(row['total_fine_amt'])
            else:
                row['total_fine_amt'] = 0.0
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fines summary: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/pay")
def pay_fines(request: PayFinesRequest):
    """
    Pay all unpaid fines for a borrower.
    
    Rules:
    - Cannot pay fines for books that are still checked out
    - Marks all relevant FINES rows as Paid = TRUE
    - No partial payments allowed
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
        
        # Check for unpaid fines on books still checked out
        check_sql = """
            SELECT COUNT(*) AS cnt
            FROM BOOK_LOANS bl
            INNER JOIN FINES f ON bl.Loan_id = f.Loan_id
            WHERE bl.Card_id = %s
            AND f.Paid = 0
            AND bl.Date_in IS NULL
        """
        cursor.execute(check_sql, (request.card_id,))
        if cursor.fetchone()['cnt'] > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pay fines for borrower {request.card_id}: some books with fines are still checked out"
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
        cursor.execute(pay_sql, (request.card_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        
        return {
            "card_id": request.card_id,
            "rows_updated": rows_affected,
            "message": f"Successfully paid fines for borrower {request.card_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error paying fines: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



