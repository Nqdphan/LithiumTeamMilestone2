"""
Borrowers router for the Library Management System API.
Handles borrower creation and management.
"""

import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import mysql.connector
from mysql.connector import Error
from db import get_connection, get_dict_cursor

router = APIRouter()


class BorrowerCreate(BaseModel):
    ssn: str = Field(..., description="Social Security Number (must be unique)")
    name: str = Field(..., description="Borrower's full name")
    address: str = Field(..., description="Borrower's address")
    phone: str = Field(..., description="Borrower's phone number")


def generate_next_card_id(cursor) -> str:
    """
    Generate the next Card_id in the format ID######.
    
    Finds the maximum Card_id matching the pattern ID######,
    extracts the numeric part, increments it, and returns the
    formatted string. If no borrowers exist, returns ID000001.
    
    Args:
        cursor: Database cursor object
        
    Returns:
        str: Next Card_id in format ID###### (e.g., ID000001, ID001000)
    """
    # Get all Card_ids that match the pattern ID######
    cursor.execute("SELECT Card_id FROM BORROWER WHERE Card_id REGEXP '^ID[0-9]{6}$'")
    results = cursor.fetchall()
    
    if not results:
        # No borrowers exist yet, start with ID000001
        return "ID000001"
    
    # Extract numeric parts and find the maximum
    max_num = 0
    for row in results:
        card_id = row['Card_id']
        # Extract the 6-digit number after "ID"
        match = re.match(r'^ID(\d{6})$', card_id)
        if match:
            num = int(match.group(1))
            max_num = max(max_num, num)
    
    # Increment and format with zero-padding
    next_num = max_num + 1
    return f"ID{next_num:06d}"


@router.post("")
def create_borrower(borrower: BorrowerCreate):
    """
    Create a new borrower.
    
    - All fields are required
    - SSN must be unique (returns 409 Conflict if duplicate)
    - Card_id is auto-generated
    
    Raises:
        HTTPException 400: If required fields are missing
        HTTPException 409: If SSN already exists
        HTTPException 500: If database error occurs
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
        
        # Application-level check: Verify SSN uniqueness before insertion
        cursor.execute("SELECT Card_id FROM BORROWER WHERE Ssn = %s", (borrower.ssn,))
        existing = cursor.fetchone()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"A borrower with SSN {borrower.ssn} already exists"
            )
        
        # Generate next Card_id in format ID######
        new_card_id = generate_next_card_id(cursor)
        
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
        # Re-raise HTTP exceptions (including our 409 for duplicate SSN)
        if conn:
            conn.rollback()
        raise
    except Error as db_error:
        # Handle MySQL database errors
        if conn:
            conn.rollback()
        
        # Check for unique constraint violation (error code 1062)
        if db_error.errno == 1062:
            # Extract SSN from error message if possible, otherwise use provided SSN
            error_msg = str(db_error.msg)
            if 'Ssn' in error_msg or 'Duplicate entry' in error_msg:
                raise HTTPException(
                    status_code=409,
                    detail=f"A borrower with SSN {borrower.ssn} already exists"
                )
            else:
                raise HTTPException(
                    status_code=409,
                    detail=f"Duplicate entry detected: {error_msg}"
                )
        else:
            # Other database errors
            raise HTTPException(
                status_code=500,
                detail=f"Database error creating borrower: {str(db_error)}"
            )
    except Exception as e:
        # Handle any other unexpected errors
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating borrower: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



