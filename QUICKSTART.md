# Quick Start Guide

## Prerequisites

Before starting, ensure you have:

- Python 3.8+ installed
- Node.js 16+ and npm installed
- MySQL database server running
- MySQL database named `library` created (create it manually if it doesn't exist)

## Backend Setup (Terminal 1)

```bash
cd backend

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your database credentials
# Create a file named .env in the backend/ directory with:
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=library

# Initialize database (creates tables and imports CSV data)
# Safe to run multiple times - only imports data if tables are empty
python init_db.py

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

Backend will be running at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

## Frontend Setup (Terminal 2)

Open a new terminal window/tab:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will be running at: `http://localhost:5173` (Vite default port) or the port shown in the terminal output.

## Running the System End-to-End

1. **Start Backend** (Terminal 1): Run `uvicorn main:app --reload --port 8000` in the `backend/` directory
2. **Start Frontend** (Terminal 2): Run `npm run dev` in the `frontend/` directory
3. **Open Browser**: Navigate to the frontend URL (typically `http://localhost:5173`)

Both servers must be running concurrently for the application to work properly.

## Testing the Application

1. Open the frontend URL (typically `http://localhost:5173`) in your browser
2. Navigate to "Search Books" and try searching for a book
3. Go to "Borrowers" to add a new borrower
4. Use "Loans" to checkout/check-in books
5. Check "Fines" to view and pay fines

## Troubleshooting

### Backend Issues

- Make sure MySQL is running
- Verify `.env` file exists in `backend/` directory with correct credentials
- Ensure database `library` exists (create it manually: `CREATE DATABASE library;`)
- Run `python init_db.py` if tables don't exist (safe to run multiple times)
- Check that `DB_PASSWORD` is set correctly in `.env`

### Frontend Issues

- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify API calls in Network tab
- Ensure frontend port matches what's shown in terminal (Vite defaults to 5173)

### Database Connection Issues

- Verify MySQL credentials in `.env` file
- Ensure MySQL server is accessible
- Check that database `library` exists
- Verify MySQL user has permissions to access the database
