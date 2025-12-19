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

# Initialize database
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
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

### Database Operations
```bash
# Reset database (WARNING: destroys all data)
rm instance/classification.db
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Import existing XML data
python migrate_existing_data.py
```

## Architecture Overview

This is a Flask web application for collaborative multi-user voting on note classifications in manuscript records. The application uses a modular Blueprint-based architecture with SQLite database backend.

### System Architecture

**Application Factory Pattern:**
- `app.py` - Creates and configures the Flask application
- Registers blueprints for modular route organization
- Initializes SQLAlchemy database connection
- Configures session management

**Database Layer (SQLAlchemy ORM):**
- `models.py` - Database models and relationships
  - `User` - User accounts with admin flag
  - `Record` - Manuscript records with bib_id
  - `Note` - Individual notes within records
  - `Vote` - User votes on note classifications
  - `Setting` - Configurable system settings
- SQLite database: `instance/classification.db`
- One vote per user per note (unique constraint)
- Cascading deletes for data integrity

**Authentication System:**
- `auth.py` - Simple username-only authentication
- No passwords required (trusted team environment)
- Session-based with 7-day persistence
- Auto-grants admin to username "Admin" (case-insensitive)
- Decorators: `@login_required`, `@admin_required`

**Route Blueprints:**

1. **`routes/main.py`** - Record browsing and navigation
   - `/` - Index page with all records
   - `/record/<bib_id>` - Record detail with voting interface
   - `/start-unclassified` - Jump to first unclassified note
   - `/next-unclassified/<bib>` - Navigate to next unclassified
   - `/next-unknown/<bib>` - Navigate to next unknown consensus
   - `/next-pending-review/<bib>` - Navigate to next unvoted note

2. **`routes/voting.py`** - Vote submission endpoints
   - `POST /vote` - Submit or update single note vote
   - `POST /vote-identical` - Bulk vote on all identical notes
   - Returns vote distribution, consensus, and voter data

3. **`routes/filters.py`** - Filtered views
   - `/unknown` - Records with "?" consensus
   - `/pending-review` - Records needing user's vote
   - `/contentious` - Records below consensus threshold

4. **`routes/admin.py`** - Admin interface (requires `@admin_required`)
   - `/admin/dashboard` - Statistics and top contributors
   - `/admin/upload` - XML import interface
   - `/admin/export` - XML export with confidence filter
   - `/admin/settings` - Configure contentious threshold and min votes

**Business Logic:**

- `utils/probability.py` - Core voting logic
  - `calculate_vote_distribution(note_id)` - Computes consensus from votes
  - `get_user_vote_for_note(user_id, note_id)` - Retrieves user's vote
  - `count_identical_notes(note_text)` - Finds duplicate notes
  - `get_identical_note_ids(note_text)` - Returns IDs of matching notes
  - Consensus calculation: highest vote count, ties broken alphabetically
  - Contentious detection: consensus < threshold AND votes >= min_votes

- `utils/xml_parser.py` - XML import functionality
  - Parses XML records and notes into database
  - Optionally creates initial votes from existing classifications
  - Idempotent: skips duplicate records

- `utils/xml_exporter.py` - XML export functionality
  - Exports records with consensus classifications
  - Filters by confidence threshold
  - Includes vote statistics as attributes

**Frontend:**
- `templates/` - Jinja2 templates with Bootstrap 5
  - `base.html` - Base template with navigation
  - `record.html` - Main voting interface
  - `login.html` - Login page
  - `admin/` - Admin interface templates
- `static/js/app.js` - Client-side JavaScript
  - Vote submission via AJAX
  - Dynamic UI updates for vote distributions
  - Keyboard navigation (← → arrow keys)
  - Vote visibility toggle
  - Bulk voting for identical notes
- `static/css/style.css` - Custom styling

### Classification System

The app supports 7 classification types for manuscript notes:
- **W** (Work) - Content related to the work itself
- **O** (Object) - Physical description of the manuscript
- **A** (Administrative) - Cataloging or processing information
- **OW** (Object/Work) - Combined physical and content description
- **AW** (Administrative/Work) - Combined administrative and content information
- **AO** (Administrative/Object) - Combined administrative and physical information
- **?** (Unknown) - Classification unclear or uncertain

### Multi-User Voting Flow

1. **User logs in** (username only, no password)
2. **Navigates to record** with notes needing classification
3. **Submits vote** by clicking classification button
4. **AJAX request** sent to `/vote` endpoint with:
   - `bib_id` - Record identifier
   - `note_index` - Note position within record
   - `classification` - Selected classification type
5. **Backend processing**:
   - Validates classification type
   - Creates or updates vote in database
   - Calculates new vote distribution
   - Determines consensus (highest vote count)
   - Checks if contentious (< threshold with >= min votes)
   - Retrieves all voters for the note
6. **JSON response** returned with:
   - Vote distribution (counts and probabilities)
   - Consensus classification and confidence
   - Contentious flag
   - Voter data (grouped by classification)
7. **Frontend updates**:
   - Vote distribution display
   - "Who Voted?" section
   - Button highlighting for user's vote
   - Success notification

### Bulk Voting for Identical Notes

1. **User checks** "Vote on all X identical notes" checkbox
2. **Submits vote** by clicking classification button
3. **AJAX request** sent to `/vote-identical` endpoint with:
   - `note_text` - Full text of the note
   - `classification` - Selected classification type
4. **Backend processing**:
   - Finds all notes with matching text
   - Creates or updates vote for each note
   - Commits all changes in single transaction
5. **JSON response** with:
   - Total notes affected
   - New votes created
   - Existing votes updated
6. **Notification** shows bulk operation summary

### Consensus Calculation Algorithm

```python
# Count votes per classification
vote_counts = {'w': 3, 'o': 2, 'a': 1}  # Example
total_votes = 6

# Calculate probabilities
probabilities = {
    'w': 3/6 = 0.50,  # 50%
    'o': 2/6 = 0.33,  # 33%
    'a': 1/6 = 0.17   # 17%
}

# Determine consensus (highest count, alphabetical tie-break)
consensus = 'w'
consensus_probability = 0.50

# Check if contentious
threshold = 0.70  # 70% from settings
min_votes = 3     # From settings
is_contentious = (total_votes >= 3 and 0.50 < 0.70)  # True
```

### Key Features

**Vote Privacy:**
- Other users' votes hidden by default
- "Show Other Votes" button toggles visibility
- Prevents vote bias before user makes decision

**Identical Notes Detection:**
- Badge shows "X identical" count
- Checkbox allows bulk voting on all identical notes
- Finds matches based on exact text comparison

**Translation Integration:**
- Translate button (🌐) next to each note
- Opens Google Translate in new tab
- Auto-detects source language
- Pre-fills note text via URL encoding

**Contentious Detection:**
- Configurable threshold (default 70%)
- Configurable minimum votes (default 3)
- Visual badge on contentious notes
- Dedicated filter page for contentious records

**Admin Auto-Grant:**
- Username "Admin" (case-insensitive) automatically gets `is_admin=True`
- Applied to both new and existing users
- No manual database updates required

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Records table
CREATE TABLE records (
    id INTEGER PRIMARY KEY,
    bib_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Notes table
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    record_id INTEGER NOT NULL REFERENCES records(id),
    note_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(record_id, note_index)
);

-- Votes table
CREATE TABLE votes (
    id INTEGER PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES notes(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    classification VARCHAR(3) NOT NULL,
    voted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(note_id, user_id)
);

-- Settings table
CREATE TABLE settings (
    id INTEGER PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(255) NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Key Files Reference

**Core Application:**
- `app.py` (50 lines) - Application factory
- `models.py` (116 lines) - Database models
- `auth.py` (77 lines) - Authentication system
- `config.py` - Configuration settings

**Route Blueprints:**
- `routes/main.py` (206 lines) - Main routes
- `routes/voting.py` (150 lines) - Vote endpoints
- `routes/filters.py` - Filter views
- `routes/admin.py` - Admin interface

**Utilities:**
- `utils/probability.py` (235 lines) - Vote calculations
- `utils/xml_parser.py` - XML import
- `utils/xml_exporter.py` - XML export

**Frontend:**
- `templates/record.html` (262 lines) - Main voting UI
- `static/js/app.js` (260 lines) - Client-side logic
- `static/css/style.css` - Custom styling

**Data:**
- `instance/classification.db` - SQLite database
- `data.xml` - XML import/export format

### Common Development Tasks

**Adding a new classification type:**
1. Update validation in `routes/voting.py` (lines 23-24)
2. Add color mapping in `utils/probability.py` (lines 196-205)
3. Update template in `templates/record.html` (buttons section)
4. Update JavaScript in `static/js/app.js` (color function)

**Adding a new filter view:**
1. Create route in `routes/filters.py`
2. Add navigation link in `templates/base.html`
3. Create template in `templates/`
4. Use `calculate_vote_distribution()` for consensus

**Modifying consensus algorithm:**
1. Edit `calculate_vote_distribution()` in `utils/probability.py`
2. Update tests if applicable
3. Consider migration for existing data

**Adding admin features:**
1. Create route in `routes/admin.py` with `@admin_required`
2. Add link to `templates/admin/dashboard.html`
3. Create template in `templates/admin/`

### Performance Considerations

**Database Queries:**
- Use `joinedload()` for eager loading votes
- Avoid N+1 queries in record lists
- Index on foreign keys (note_id, user_id)

**Caching Opportunities:**
- Vote distributions (invalidate on vote update)
- Identical note counts (invalidate on data import)
- User session data

**Optimization Tips:**
- Batch vote operations for identical notes
- Use database-level consensus calculation for large datasets
- Consider materialized views for statistics

### Common Issues

**Port 5000 Conflicts (macOS):**
- AirPlay Receiver service uses port 5000
- Solution: Use `python -c "from app import app; app.run(debug=True, port=8080)"`
- Alternative: Disable AirPlay Receiver in System Preferences

**Database Locked Errors:**
- SQLite doesn't handle concurrent writes well
- Enable WAL mode: `PRAGMA journal_mode=WAL;`
- Consider PostgreSQL for production

**Vote Display Not Updating:**
- Check browser console for JavaScript errors
- Verify voters data included in JSON response
- Ensure `updateVotersDisplay()` function called

**Import Failures:**
- Verify XML is well-formed UTF-8
- Check for duplicate bib_id attributes
- Ensure special characters are properly encoded

### Testing

**Manual Testing Checklist:**
1. Login as regular user and admin
2. Vote on notes, verify distribution updates
3. Change vote, verify update works
4. Bulk vote on identical notes
5. Check contentious detection with different thresholds
6. Import XML file
7. Export with different confidence thresholds
8. Test translation button
9. Navigate with keyboard arrows
10. Check all filter views

**Database Testing:**
```python
# Test vote creation
from app import app, db
from models import User, Note, Vote

with app.app_context():
    user = User.query.first()
    note = Note.query.first()
    vote = Vote(note_id=note.id, user_id=user.id, classification='w')
    db.session.add(vote)
    db.session.commit()
```

### Security Considerations

**Authentication:**
- No passwords = low security
- Suitable for trusted team environments only
- Consider adding password support for production

**Admin Access:**
- Auto-grant based on username is convenient but insecure
- Anyone can become admin by using "Admin" username
- Fine for internal tools, not for public deployment

**Input Validation:**
- Classification types validated server-side
- Username length limited to 50 characters
- Note text properly escaped in templates

**SQL Injection:**
- Protected by SQLAlchemy ORM
- Never concatenate raw SQL with user input

### Future Enhancements

**Potential Features:**
- Email notifications for contentious notes
- Comment system for discussing classifications
- Vote change history/audit log
- Export to CSV for analysis
- REST API for external integrations
- PostgreSQL support for better concurrency
- Real-time updates with WebSockets
- Mobile-responsive improvements
- Keyboard shortcuts for voting (1-7 keys)
- Undo last vote action

**Performance Improvements:**
- Redis caching layer
- Background job queue for bulk operations
- Database query optimization with indexes
- Frontend pagination for large record sets

### Migration Notes

**From XML-based single-user system:**
1. Old system stored classifications directly in XML
2. New system uses database with voting
3. Migration script: `migrate_existing_data.py`
4. Preserves existing classifications as "Admin" votes
5. XML import/export maintains compatibility
