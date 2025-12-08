"""
Borrowers router for the Library Management System API.
Handles borrower creation and management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from db import get_connection, get_dict_cursor

router = APIRouter()


class BorrowerCreate(BaseModel):
    ssn: str = Field(..., description="Social Security Number (must be unique)")
    name: str = Field(..., description="Borrower's full name")
    address: str = Field(..., description="Borrower's address")
    phone: str = Field(..., description="Borrower's phone number")


@router.post("")
def create_borrower(borrower: BorrowerCreate):
    """
    Create a new borrower.
    
    - All fields are required
    - SSN must be unique (returns 400 if duplicate)
    - Card_id is auto-generated
    """
    # Validate inputs
    if not borrower.ssn or not borrower.name or not borrower.address or not borrower.phone:
        raise HTTPException(
            status_code=400,
            detail="All borrower fields (SSN, name, address, phone) must be non-empty"
        )
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        # Check if SSN already exists
        cursor.execute("SELECT Card_id FROM BORROWER WHERE Ssn = %s", (borrower.ssn,))
        existing = cursor.fetchone()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"A borrower with SSN {borrower.ssn} already exists"
            )
        
        # Get next Card_id
        cursor.execute("SELECT MAX(CAST(Card_id AS UNSIGNED)) AS max_id FROM BORROWER")
        result = cursor.fetchone()
        new_card_id = str((result['max_id'] or 0) + 1)
        
        # Insert new borrower
        insert_sql = """
            INSERT INTO BORROWER (Card_id, Ssn, Bname, Address, Phone)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (new_card_id, borrower.ssn, borrower.name, borrower.address, borrower.phone))
        conn.commit()
        
        return {
            "card_id": new_card_id,
            "message": "Borrower created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating borrower: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



