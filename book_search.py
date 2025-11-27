"""
Book search functionality for the Library Management System.
Provides case-insensitive search across books, titles, and authors.
"""

from db import get_connection, get_dict_cursor


def search_books(query: str) -> list[dict]:
    """
    Case-insensitive substring search across:
      - BOOK.Isbn
      - BOOK.Title
      - AUTHORS.Name (via BOOK_AUTHORS)

    Returns a list of dicts, each with:
      - 'isbn': Book ISBN
      - 'title': Book title
      - 'authors': Comma-separated author names, alphabetically sorted
      - 'status': 'IN' or 'OUT'

    A book is 'OUT' if any row in BOOK_LOANS for that ISBN has Date_in IS NULL,
    otherwise it is 'IN'.
    
    Args:
        query: Search string to match against ISBN, title, or author name
        
    Returns:
        list[dict]: List of matching books with their details
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        
        search_pattern = f"%{query.lower()}%"
        
        sql = """
            SELECT 
                b.Isbn AS isbn,
                b.Title AS title,
                GROUP_CONCAT(DISTINCT a.Name ORDER BY a.Name SEPARATOR ', ') AS authors,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 
                        FROM BOOK_LOANS bl 
                        WHERE bl.Isbn = b.Isbn 
                        AND bl.Date_in IS NULL
                    ) THEN 'OUT'
                    ELSE 'IN'
                END AS status
            FROM BOOK b
            LEFT JOIN BOOK_AUTHORS ba ON b.Isbn = ba.Isbn
            LEFT JOIN AUTHORS a ON ba.Author_id = a.Author_id
            WHERE 
                LOWER(b.Isbn) LIKE %s
                OR LOWER(b.Title) LIKE %s
                OR LOWER(a.Name) LIKE %s
            GROUP BY b.Isbn, b.Title
            ORDER BY b.Title
        """
        
        cursor.execute(sql, (search_pattern, search_pattern, search_pattern))
        results = cursor.fetchall()
        
        # Handle NULL authors (books with no authors in the database)
        for row in results:
            if row['authors'] is None:
                row['authors'] = ''
        
        return results
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


