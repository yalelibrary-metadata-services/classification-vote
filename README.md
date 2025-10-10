# Classification Vote Web App

A Flask web application for voting on note classifications in XML records.

## Features

- Load XML records with notes
- Interactive interface for classifying notes as:
  - **Work (W)**: Content related to the work itself
  - **Object (O)**: Physical description of the manuscript
  - **Administrative (A)**: Cataloging or processing information
  - **Object/Work (OW)**: Combined physical and content description
  - **Administrative/Work (AW)**: Combined administrative and content information
  - **Administrative/Object (AO)**: Combined administrative and physical information
  - **Unknown (?)**: Classification unclear or uncertain
- Real-time updates to XML file
- Record navigation with Previous/Next buttons and progress meter
- Visual progress bar showing completion percentage through records
- Keyboard shortcuts (← → arrow keys) for navigation
- Filter view for records with unknown classifications
- Responsive Bootstrap UI

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Ensure you have a `data.xml` file in the root directory with your records

3. Run the application:
   ```bash
   source venv/bin/activate
   python app.py
   ```

4. Open your browser to `http://localhost:5000`

### Port 5000 Issues (macOS)

If you encounter a "Port 5000 is in use" error on macOS, this is because AirPlay Receiver uses port 5000 by default.

**Option 1: Use a different port**
```bash
source venv/bin/activate
python -c "from app import app; app.run(debug=True, port=8080)"
```
Then visit `http://localhost:8080`

**Option 2: Disable AirPlay Receiver**
Go to **System Preferences → General → AirDrop & Handoff** and turn off "AirPlay Receiver"

## Usage

1. The home page shows all available records
2. Click "Classify Notes" on any record to view its notes
3. For each note, click the appropriate classification button (W, O, A, OW, AW, AO, or ?)
4. Classifications are automatically saved to the XML file
5. The current classification is displayed under each note
6. Use Previous/Next buttons or arrow keys (← →) to navigate between records
7. View progress meter to see your completion percentage through all records
8. Click "Unknown" in the navigation or "View Unknown Classifications" on the home page to see records needing review

## XML Format

The application expects XML with this structure:

```xml
<?xml version='1.0' encoding='utf-8'?>
<records>
  <record bib="unique_id">
    <title>Record title</title>
    <note type="existing_type">Note content</note>
    <!-- More notes... -->
  </record>
</records>
```