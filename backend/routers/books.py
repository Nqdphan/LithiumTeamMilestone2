"""
Books router for the Library Management System API.
Handles book search operations.
"""

from fastapi import APIRouter, HTTPException, Query
from db import get_connection, get_dict_cursor

router = APIRouter()


@router.get("/search")
def search_books(q: str = Query(..., description="Search query for ISBN, title, or author name")):
    """
    Search for books by ISBN, title, or author name.
    
    Returns books with:
    - isbn: Book ISBN
    - title: Book title
    - authors: Comma-separated author names
    - checked_out: Boolean indicating if book is checked out
    - borrower_id: Card_id if checked out, None otherwise
    """
    if not q:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        search_pattern = f"%{q.lower()}%"
        
        sql = """
            SELECT 
                b.Isbn AS isbn,
                b.Title AS title,
                GROUP_CONCAT(DISTINCT a.Name ORDER BY a.Name SEPARATOR ', ') AS authors,
                MAX(CASE 
                    WHEN bl.Loan_id IS NOT NULL AND bl.Date_in IS NULL THEN 1
                    ELSE 0
                END) AS checked_out,
                MAX(CASE 
                    WHEN bl.Loan_id IS NOT NULL AND bl.Date_in IS NULL THEN bl.Card_id
                    ELSE NULL
                END) AS borrower_id
            FROM BOOK b
            LEFT JOIN BOOK_AUTHORS ba ON b.Isbn = ba.Isbn
            LEFT JOIN AUTHORS a ON ba.Author_id = a.Author_id
            LEFT JOIN BOOK_LOANS bl ON b.Isbn = bl.Isbn AND bl.Date_in IS NULL
            WHERE 
                LOWER(b.Isbn) LIKE %s
                OR LOWER(b.Title) LIKE %s
                OR LOWER(a.Name) LIKE %s
            GROUP BY b.Isbn, b.Title
            ORDER BY b.Title
        """
        
        cursor.execute(sql, (search_pattern, search_pattern, search_pattern))
        results = cursor.fetchall()
        
        # Handle NULL authors
        for row in results:
            if row['authors'] is None:
                row['authors'] = ''
            row['checked_out'] = bool(row['checked_out'])
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching books: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

