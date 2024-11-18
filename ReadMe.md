# Backend Server Setup Instructions

## Step 1: Install Dependencies
1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv env
   ```
2. Activate the virtual environment:
   - On Windows:
     ```bash
     .\env\Scripts\activate
     ```
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 2: Navigate to the Server Folder

## Step 3: Run Backend Server

```bash
   cd server && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```


