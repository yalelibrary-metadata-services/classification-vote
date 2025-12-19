# Setup Instructions

## Environment Setup

### 1. Create Virtual Environment

**Using Python venv:**
```bash
python -m venv venv
```

**Using uv (recommended if available):**
```bash
uv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

**Using pip:**
```bash
pip install -r requirements.txt
```

**Using uv:**
```bash
uv pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 5. Initialize Database (First Run)

The database will be automatically created on first run. To import data:

**Option A: Use migration script (if you have data.xml)**
```bash
python migrate_existing_data.py
```

**Option B: Use admin interface**
1. Login as "Admin" (case-insensitive)
2. Go to Admin → Upload XML
3. Upload your XML file

## Notes

- Database file: `instance/classification.db` (created automatically)
- Default admin: Login with username "Admin" (case-insensitive)
- Port: 5000 (change in `app.py` if needed)

