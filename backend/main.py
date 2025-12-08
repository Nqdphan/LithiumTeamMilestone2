"""
FastAPI main application for the Library Management System.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import books, borrowers, loans, fines

app = FastAPI(title="Library Management System API", version="1.0.0")

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(borrowers.router, prefix="/borrowers", tags=["borrowers"])
app.include_router(loans.router, prefix="/loans", tags=["loans"])
app.include_router(fines.router, prefix="/fines", tags=["fines"])


@app.get("/")
def root():
    """Root endpoint to check API status."""
    return {"status": "ok", "message": "Library backend running"}



