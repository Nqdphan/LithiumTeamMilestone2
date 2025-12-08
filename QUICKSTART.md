# Quick Start Guide

## Backend Setup (Terminal 1)

```bash
cd backend

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your database credentials
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=library

# Initialize database (first time only)
python init_db.py

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

Backend will be running at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

## Frontend Setup (Terminal 2)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will be running at: `http://localhost:3000` (or the port shown)

## Testing the Application

1. Open `http://localhost:3000` in your browser
2. Navigate to "Search Books" and try searching for a book
3. Go to "Borrowers" to add a new borrower
4. Use "Loans" to checkout/check-in books
5. Check "Fines" to view and pay fines

## Troubleshooting

### Backend Issues
- Make sure MySQL is running
- Verify `.env` file exists in `backend/` directory
- Check that database `library` exists
- Run `python init_db.py` if tables don't exist

### Frontend Issues
- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify API calls in Network tab

### Database Connection Issues
- Verify MySQL credentials in `.env`
- Ensure MySQL server is accessible
- Check that database `library` exists



