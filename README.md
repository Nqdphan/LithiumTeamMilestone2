# Library Management System

## Prerequisites

Before starting, ensure you have:

- Python 3.8+ installed
- Node.js 16+ and npm installed
- MySQL database server running
- MySQL database named `library` created (create it manually if it doesn't exist: `CREATE DATABASE library;`)

The instructions assume a Linux system. You might need to use different directory navigation and Python commands on a different OS.

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

### 2. Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

For how to run the application, check the **Quick Start Guide**.
