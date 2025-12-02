# Library Management System (CS 4347 Milestone 2)

## Overview

This is a MySQL + Python Library Management System that provides functionality for:

- **Searching books** by ISBN, title, or author name
- **Managing book checkouts and check-ins** (loans)
- **Tracking borrowers** and their information
- **Calculating and managing fines** for overdue books

The system uses a MySQL database to store all data and provides an interactive command-line interface (CLI) for all operations.

## Prerequisites

Before running the system, ensure you have:

1. **Python 3.x** installed (Python 3.7 or higher recommended)
2. **MySQL Server** installed and running
3. **Python dependencies** installed:
   - `mysql-connector-python` (for MySQL connectivity)
   - `python-dotenv` (for environment variable management)

The MySQL user specified in your `.env` file must have permissions to create tables and foreign key constraints.

## Setup Steps

### 1. Create MySQL Database

Create a MySQL database named `library`:

```sql
CREATE DATABASE library;
```

### 2. Configure Database Connection

The system uses environment variables for database credentials. Create a `.env` file in the project root directory with the following variables:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library
```

The `.env` file must be located in the same directory as `main.py`.

**Important**: Replace `your_mysql_password` with your actual MySQL root password (or the password for the user specified in `DB_USER`).

### 3. Install Python Dependencies

Install the required Python packages:

```bash
pip3 install -r requirements.txt
```

Or install manually:

```bash
pip3 install mysql-connector-python python-dotenv
```

If you encounter `ModuleNotFoundError`, reinstall dependencies using `pip3 install -r requirements.txt`.

### 4. Verify CSV Files

Ensure the following CSV files are present in the project root directory (same folder as `main.py`):

- `book.csv` - Contains book data (ISBN, Title)
- `authors.csv` - Contains author data (Author_id, Name)
- `book_authors.csv` - Contains book-author relationships (Author_id, Isbn)
- `borrower.csv` - Contains borrower data (Card_id, Ssn, Bname, Address, Phone)

All CSV files should have header rows matching the column names above.

The headers must match exactly (case-sensitive). Incorrect headers will cause import failures.

## How to Run

### First Run

The program automatically loads `.env` using `python-dotenv`. No additional configuration is required.

Simply execute:

```bash
python3 main.py
```

On the first run, the program will:

1. **Connect to MySQL** using the credentials from your `.env` file
2. **Create all necessary tables** if they don't exist:
   - `BOOK` - Stores book information
   - `AUTHORS` - Stores author information
   - `BORROWER` - Stores borrower information
   - `BOOK_AUTHORS` - Links books to their authors
   - `BOOK_LOANS` - Tracks book checkouts and check-ins
   - `FINES` - Tracks fines for overdue books
3. **Import data from CSV files** if the tables are empty:
   - Data from `book.csv` → `BOOK` table
   - Data from `authors.csv` → `AUTHORS` table
   - Data from `book_authors.csv` → `BOOK_AUTHORS` table
   - Data from `borrower.csv` → `BORROWER` table
4. **Launch the CLI menu** for interacting with the system

You will see informative messages during initialization, such as:

- "Creating tables if not exist..."
- "BOOK table is empty. Importing from CSV..."
- "✓ Imported 25001 rows into BOOK."
- etc.

### Subsequent Runs

On subsequent runs, simply execute:

```bash
python3 main.py
```

The program will:

1. **Check if tables already have data**
2. **Skip CSV imports** if data already exists (prevents duplicates)
3. **Go straight to the CLI menu**

You will see messages like:

- "BOOK already has data, skipping import."
- "AUTHORS already has data, skipping import."
- etc.

## Using the CLI Menu

Once the program starts, you'll see a menu with the following options:

```
===== Library Management System =====
1. Search books
2. Checkout book
3. Check-in book
4. Add borrower
5. Update fines
6. View fines
7. Exit
Enter your choice:
```

1. **Search books** - Search for books by ISBN, title, or author name
2. **Checkout book** - Check out a book to a borrower
3. **Check-in book** - Return a checked-out book
4. **Add borrower** - Add a new borrower to the system
5. **Update fines** - Calculate fines for all overdue loans
6. **View fines** - View fines for borrowers (with option to pay)
7. **Exit** - Exit the program

Follow the on-screen prompts to use each feature.

## Notes for TA

### What You DON'T Need to Do

- ❌ Manually create tables using SQL scripts
- ❌ Manually import CSV files using MySQL commands
- ❌ Run separate initialization scripts
- ❌ Worry about duplicate data imports

### What You DO Need to Do

1. ✅ Ensure MySQL Server is running
2. ✅ Create the `library` database (if it doesn't exist)
3. ✅ Create a `.env` file with your MySQL credentials
4. ✅ Ensure all CSV files are in the project root directory
5. ✅ Run `python3 main.py`

That's it! The system handles everything else automatically.

### Troubleshooting

**MySQL command not found**

If your system reports `mysql: command not found`, ensure MySQL is installed (via Homebrew on macOS or via the MySQL installer).

**Connection Error**:

- Verify MySQL is running: `mysql -u root -p`
- Check your `.env` file has correct credentials
- Ensure the `library` database exists

**CSV Import Errors**:

- Verify all CSV files exist in the project root
- Check CSV files have proper headers
- Ensure CSV files are readable (permissions)

**Table Already Exists Errors**:

- This is normal if tables were created previously
- The system uses `CREATE TABLE IF NOT EXISTS`, so it's safe

## Database Schema

The system uses the following tables:

- **BOOK**: `Isbn` (PK), `Title`
- **AUTHORS**: `Author_id` (PK), `Name`
- **BORROWER**: `Card_id` (PK), `Ssn`, `Bname`, `Address`, `Phone`
- **BOOK_AUTHORS**: `Author_id` (PK, FK), `Isbn` (PK, FK)
- **BOOK_LOANS**: `Loan_id` (PK, AUTO_INCREMENT), `Isbn` (FK), `Card_id` (FK), `Date_out`, `Due_date`, `Date_in`
- **FINES**: `Loan_id` (PK, FK), `Fine_amt`, `Paid`

All foreign key constraints are enforced by MySQL.

## Resetting the Database

If you need to reset the database and re-import all data:

1. Drop all tables manually in MySQL:

   ```sql
   USE library;
   DROP TABLE IF EXISTS FINES;
   DROP TABLE IF EXISTS BOOK_LOANS;
   DROP TABLE IF EXISTS BOOK_AUTHORS;
   DROP TABLE IF EXISTS BORROWER;
   DROP TABLE IF EXISTS BOOK;
   DROP TABLE IF EXISTS AUTHORS;
   ```

2. Run `python3 main.py` again - it will recreate tables and import data.

**Note**: The system does NOT automatically drop tables. This is intentional to prevent accidental data loss.

## Project Structure

```
LithiumTeam/
├── main.py              # Main CLI menu and entry point
├── init_db.py           # Database initialization and CSV import
├── db.py                # Database connection utilities
├── book_search.py       # Book search functionality
├── borrowers.py         # Borrower management
├── loans.py             # Loan (checkout/check-in) management
├── fines.py             # Fine calculation and management
├── requirements.txt     # Python dependencies
├── .env                 # Database credentials (create this)
├── book.csv             # Book data
├── authors.csv          # Author data
├── book_authors.csv     # Book-author relationships
└── borrower.csv         # Borrower data
```

## License

This project is part of CS 4347 Milestone 2 coursework.
