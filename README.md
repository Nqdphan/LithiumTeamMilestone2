# Library Management System - Full Stack Application

A full-stack library management system built with **FastAPI** (Python backend) and **React** (frontend).

## Project Structure

```
LithiumTeam/
├── backend/                 # FastAPI backend
│   ├── routers/            # API route handlers
│   │   ├── books.py
│   │   ├── borrowers.py
│   │   ├── loans.py
│   │   └── fines.py
│   ├── db/                 # Database connection module
│   │   └── __init__.py
│   ├── init_db.py          # Database initialization and CSV import
│   ├── main.py             # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── *.csv               # Data files (book.csv, authors.csv, etc.)
│
└── frontend/               # React frontend (Vite)
    ├── src/
    │   ├── pages/          # Page components
    │   │   ├── SearchBooks.jsx
    │   │   ├── Borrowers.jsx
    │   │   ├── Loans.jsx
    │   │   └── Fines.jsx
    │   ├── api.js          # API client
    │   └── App.jsx         # Main app component with routing
    └── package.json
```

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- MySQL database server
- MySQL database named `library` (or configure in `.env`)

## Setup Instructions

### 1. Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend/` directory with your database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=library
```

5. Initialize the database (creates tables and imports CSV data):

```bash
python init_db.py
```

6. Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

### 2. Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` (or the port shown in the terminal)

## API Endpoints

### Books

- `GET /books/search?q={query}` - Search books by ISBN, title, or author

### Borrowers

- `POST /borrowers` - Create a new borrower

### Loans

- `POST /loans/checkout` - Checkout a book
- `GET /loans/open` - Get open loans (with optional filters)
- `POST /loans/checkin` - Check in a book by loan ID

### Fines

- `POST /fines/update` - Update fines for all overdue loans
- `GET /fines/summary` - Get fines summary by borrower
- `POST /fines/pay` - Pay all fines for a borrower

## Features

### Search Books

- Search by ISBN, title, or author name
- View book availability status
- See borrower information for checked-out books

### Borrowers

- Add new borrowers to the system
- Automatic Card ID generation
- SSN uniqueness validation

### Loans

- Checkout books with validation:
  - Book must be available
  - Borrower must have < 3 active loans
  - Borrower must have no unpaid fines
- Check-in books by loan ID
- Search open loans by ISBN, Card ID, or borrower name

### Fines

- Automatic fine calculation ($0.25 per day late)
- View fines summary by borrower
- Pay fines (only for returned books)

## Development

### Backend Development

- The backend uses FastAPI with automatic API documentation
- Visit `http://localhost:8000/docs` for interactive API documentation
- CORS is configured to allow requests from `http://localhost:3000`

### Frontend Development

- Built with React and Vite for fast development
- Uses React Router for navigation
- API calls are centralized in `src/api.js`

## Notes

- The database schema is defined in `backend/init_db.py`
- CSV files are imported automatically on first run if tables are empty
- All database operations use transactions for data integrity
- The frontend expects the backend to be running on port 8000
