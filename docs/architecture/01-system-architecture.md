# System Architecture Overview

## Purpose
High-level view of all system components and their relationships, showing how data flows from the client browser through the Flask application to the database.

## Diagram

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser["Browser<br/>(Chrome/Firefox/Safari)"]
        Bootstrap["Bootstrap 5<br/>UI Framework"]
        JS["JavaScript<br/>(app.js)"]
        AJAX["AJAX Requests"]
    end

    subgraph FlaskApp["Flask Application Layer"]
        AppFactory["app.py<br/>Application Factory"]
        Session["Session Management<br/>(7-day cookies)"]
        Config["config.py<br/>Configuration"]
    end

    subgraph Routing["Routing Layer (Blueprints)"]
        AuthBP["auth.py<br/>Authentication"]
        MainBP["routes/main.py<br/>Record Browsing"]
        VotingBP["routes/voting.py<br/>Vote Endpoints"]
        FiltersBP["routes/filters.py<br/>Filter Views"]
        AdminBP["routes/admin.py<br/>Admin Interface"]
    end

    subgraph BusinessLogic["Business Logic Layer"]
        Probability["utils/probability.py<br/>Consensus Calculation"]
        XMLParser["utils/xml_parser.py<br/>XML Import"]
        XMLExporter["utils/xml_exporter.py<br/>XML Export"]
    end

    subgraph DataLayer["Data Access Layer"]
        Models["models.py<br/>SQLAlchemy ORM"]
        UserModel["User Model"]
        RecordModel["Record Model"]
        NoteModel["Note Model"]
        VoteModel["Vote Model"]
        SettingModel["Setting Model"]
    end

    subgraph Database["Persistence Layer"]
        SQLite["SQLite Database<br/>(classification.db)"]
        WAL["WAL Mode<br/>(Write-Ahead Logging)"]
    end

    subgraph External["External Services"]
        GoogleTranslate["Google Translate<br/>(via URL)"]
    end

    Browser --> Bootstrap
    Browser --> JS
    JS --> AJAX
    AJAX -->|HTTP POST/GET| AppFactory
    AppFactory --> Session
    AppFactory --> Config
    AppFactory --> AuthBP
    AppFactory --> MainBP
    AppFactory --> VotingBP
    AppFactory --> FiltersBP
    AppFactory --> AdminBP
    
    AuthBP -->|@login_required<br/>@admin_required| MainBP
    AuthBP -->|@login_required<br/>@admin_required| VotingBP
    AuthBP -->|@login_required<br/>@admin_required| FiltersBP
    AuthBP -->|@admin_required| AdminBP
    
    VotingBP --> Probability
    AdminBP --> XMLParser
    AdminBP --> XMLExporter
    XMLParser --> Probability
    
    MainBP --> Models
    VotingBP --> Models
    FiltersBP --> Models
    AdminBP --> Models
    Probability --> Models
    
    Models --> UserModel
    Models --> RecordModel
    Models --> NoteModel
    Models --> VoteModel
    Models --> SettingModel
    
    UserModel --> SQLite
    RecordModel --> SQLite
    NoteModel --> SQLite
    VoteModel --> SQLite
    SettingModel --> SQLite
    
    SQLite --> WAL
    
    Browser -.->|External Link| GoogleTranslate

    style Client fill:#e1f5ff
    style FlaskApp fill:#fff4e1
    style Routing fill:#ffe1f5
    style BusinessLogic fill:#e1ffe1
    style DataLayer fill:#f5e1ff
    style Database fill:#ffe1e1
    style External fill:#e1ffff
```

## Component Descriptions

### Client Layer
- **Browser**: Standard web browser rendering HTML/CSS/JavaScript
- **Bootstrap 5**: UI framework providing responsive components and styling
- **JavaScript (app.js)**: Client-side logic handling vote submissions, UI updates, keyboard navigation
- **AJAX Requests**: Asynchronous HTTP requests for voting without page reloads

### Flask Application Layer
- **app.py**: Application factory pattern creating and configuring Flask app
- **Session Management**: Flask sessions stored in cookies, 7-day persistence
- **config.py**: Centralized configuration (database URI, session settings, thresholds)

### Routing Layer (Blueprints)
- **auth.py**: Authentication blueprint providing login/logout and decorators
- **routes/main.py**: Main routes for browsing records, navigation
- **routes/voting.py**: AJAX endpoints for vote submission (single and bulk)
- **routes/filters.py**: Filtered views (unknown, pending review, contentious)
- **routes/admin.py**: Admin-only routes (dashboard, XML import/export, settings)

### Business Logic Layer
- **utils/probability.py**: Core voting logic - consensus calculation, contentious detection, vote distribution
- **utils/xml_parser.py**: XML import functionality parsing records and notes
- **utils/xml_exporter.py**: XML export with confidence threshold filtering

### Data Access Layer
- **models.py**: SQLAlchemy ORM models defining database schema
- Models: User, Record, Note, Vote, Review, Setting

### Persistence Layer
- **SQLite Database**: File-based database (`instance/classification.db`)
- **WAL Mode**: Write-Ahead Logging enabled for better concurrency

### External Services
- **Google Translate**: External link for translating foreign language notes

## Key Data Flows

### Vote Submission Flow
1. User clicks classification button in browser
2. JavaScript captures event and sends AJAX POST to `/vote`
3. Flask routes to `routes/voting.py`
4. `@login_required` decorator checks session
5. Route validates input and queries database via models
6. Vote created/updated in database
7. `utils/probability.py` calculates new distribution
8. JSON response returned with consensus data
9. JavaScript updates UI dynamically

### Authentication Flow
1. User submits username on login page
2. `auth.py` checks/creates User record
3. Session created with username, user_id, is_admin
4. Session cookie set with 7-day expiration
5. All protected routes check session via decorators

### XML Import Flow
1. Admin uploads XML file via admin interface
2. `routes/admin.py` receives file
3. `utils/xml_parser.py` parses XML
4. Creates Record and Note records via models
5. Optionally creates initial Vote records
6. Commits transaction to database

## Security Considerations

- **Authentication**: Username-only (no passwords) - suitable for trusted team environments
- **Session Management**: Flask sessions with HTTP-only cookies
- **Authorization**: `@admin_required` decorator protects admin routes
- **Input Validation**: Classification types validated server-side
- **SQL Injection**: Protected by SQLAlchemy ORM

## Performance Considerations

- **Database Queries**: Uses `joinedload()` for eager loading to avoid N+1 queries
- **WAL Mode**: Enables better concurrent read performance
- **AJAX**: Asynchronous requests prevent full page reloads
- **Indexes**: Foreign keys and unique constraints are indexed

## Scalability Notes

- **SQLite Limitations**: Single-writer limitation, but WAL mode improves concurrency
- **Future Migration**: Can migrate to PostgreSQL for better multi-user performance
- **Caching Opportunities**: Vote distributions could be cached (invalidate on vote updates)
