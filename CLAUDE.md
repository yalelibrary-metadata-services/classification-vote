# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start development server (default port 5000)
source venv/bin/activate
python app.py

# If port 5000 is in use (common on macOS due to AirPlay Receiver):
python -c "from app import app; app.run(debug=True, port=8080)"

# App runs on http://localhost:5000 or http://localhost:8080
```

## Architecture Overview

This is a Flask web application for voting on note classifications in XML manuscript records. The application follows a simple MVC pattern:

### Core Components

**Data Layer (`app.py`):**
- `load_xml_data()` / `save_xml_data()` - XML file I/O operations
- `get_records()` - Parses XML into Python data structures
- XML structure: `<records>` → `<record bib="id">` → `<title>` + multiple `<note type="classification">`

**Web Layer (`app.py`):**
- `/` - Lists all records with basic info and navigation to unknown records
- `/record/<bib_id>` - Shows record details with note classification interface
- `/vote` (POST) - AJAX endpoint for updating note classifications
- `/unknown` - Filters and displays records with "?" classifications
- Record navigation: prev/next buttons with keyboard support (arrow keys)

**Frontend:**
- `templates/` - Jinja2 templates with Bootstrap UI
- `static/js/app.js` - AJAX voting, keyboard navigation, notifications
- `static/css/style.css` - Custom styling for voting interface

### Classification System

The app supports 7 classification types for manuscript notes:
- **W** (Work) - Content related to the work itself
- **O** (Object) - Physical description of the manuscript
- **A** (Administrative) - Cataloging or processing information  
- **OW** (Object/Work) - Combined physical and content description
- **AW** (Administrative/Work) - Combined administrative and content information
- **AO** (Administrative/Object) - Combined administrative and physical information
- **?** (Unknown) - Classification unclear or uncertain

### Data Flow

1. XML records loaded into memory on each request
2. User votes on note classifications via AJAX
3. XML file updated immediately with new `type` attribute
4. Frontend shows real-time feedback and updates display

### Key Files

- `data.xml` - Source XML file with manuscript records (user-provided)
- `app.py` - Main Flask application (single file)
- `templates/record.html` - Note classification voting interface
- `templates/unknown.html` - Unknown classifications filter view
- `static/js/app.js` - Client-side voting and navigation logic
- `static/css/style.css` - Custom styling including progress meter

### Navigation and Progress Features

- Sequential record browsing with prev/next buttons
- Keyboard shortcuts (← → arrow keys) for navigation
- Sticky navigation bar shows current position (e.g., "Record 5 of 42")
- Visual progress meter with completion percentage
- Progress bar updates as you navigate through records
- Navigation preserves classification progress across records

### Unknown Records Management

- `/unknown` route filters records with "?" classifications
- Dedicated UI showing preview of unknown notes
- Direct links from unknown view to record classification
- Navigation menu badge indicates unknown records need review
- Helps systematically identify and resolve uncertain classifications

### Common Issues

**Port 5000 Conflicts (macOS):**
- AirPlay Receiver service often uses port 5000
- Solution: Use `python -c "from app import app; app.run(debug=True, port=8080)"`
- Alternative: Disable AirPlay Receiver in System Preferences