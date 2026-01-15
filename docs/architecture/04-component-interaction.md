# Component Interaction Diagram

## Purpose
Shows how Flask blueprints, utilities, and models interact across different layers of the application.

## Diagram

```mermaid
graph TB
    subgraph Presentation["Presentation Layer"]
        Templates["Templates<br/>(Jinja2)"]
        StaticJS["static/js/app.js"]
        StaticCSS["static/css/style.css"]
    end

    subgraph Routing["Routing Layer (Blueprints)"]
        AuthBP["auth.py"]
        MainBP["routes/main.py"]
        VotingBP["routes/voting.py"]
        FiltersBP["routes/filters.py"]
        AdminBP["routes/admin.py"]
    end

    subgraph BusinessLogic["Business Logic Layer"]
        Probability["utils/probability.py"]
        XMLParser["utils/xml_parser.py"]
        XMLExporter["utils/xml_exporter.py"]
        SeedData["utils/seed_data.py"]
    end

    subgraph DataAccess["Data Access Layer"]
        Models["models.py<br/>(SQLAlchemy)"]
        UserModel["User Model"]
        RecordModel["Record Model"]
        NoteModel["Note Model"]
        VoteModel["Vote Model"]
        ReviewModel["Review Model"]
        SettingModel["Setting Model"]
    end

    subgraph Core["Core Application"]
        AppFactory["app.py"]
        Config["config.py"]
    end

    subgraph Database["Database"]
        SQLite["SQLite<br/>(classification.db)"]
    end

    %% Presentation to Routing
    Templates -->|Renders| MainBP
    Templates -->|Renders| FiltersBP
    Templates -->|Renders| AdminBP
    Templates -->|Renders| AuthBP
    StaticJS -->|AJAX Calls| VotingBP
    StaticJS -->|AJAX Calls| MainBP

    %% Core Application
    AppFactory -->|Registers| AuthBP
    AppFactory -->|Registers| MainBP
    AppFactory -->|Registers| VotingBP
    AppFactory -->|Registers| FiltersBP
    AppFactory -->|Registers| AdminBP
    AppFactory -->|Uses| Config
    AppFactory -->|Initializes| Models

    %% Authentication Flow
    AuthBP -->|Provides| MainBP
    AuthBP -->|Provides| VotingBP
    AuthBP -->|Provides| FiltersBP
    AuthBP -->|Provides| AdminBP
    AuthBP -->|@login_required| MainBP
    AuthBP -->|@login_required| VotingBP
    AuthBP -->|@admin_required| AdminBP
    AuthBP -->|Queries| UserModel

    %% Main Routes
    MainBP -->|Calls| Probability
    MainBP -->|Queries| RecordModel
    MainBP -->|Queries| NoteModel
    MainBP -->|Queries| VoteModel

    %% Voting Routes
    VotingBP -->|Calls| Probability
    VotingBP -->|Queries| RecordModel
    VotingBP -->|Queries| NoteModel
    VotingBP -->|Creates/Updates| VoteModel

    %% Filter Routes
    FiltersBP -->|Calls| Probability
    FiltersBP -->|Queries| RecordModel
    FiltersBP -->|Queries| NoteModel
    FiltersBP -->|Queries| VoteModel

    %% Admin Routes
    AdminBP -->|Calls| XMLParser
    AdminBP -->|Calls| XMLExporter
    AdminBP -->|Calls| Probability
    AdminBP -->|Queries| UserModel
    AdminBP -->|Queries| RecordModel
    AdminBP -->|Queries| NoteModel
    AdminBP -->|Queries| VoteModel
    AdminBP -->|Queries| SettingModel
    AdminBP -->|Updates| SettingModel

    %% Business Logic Dependencies
    Probability -->|Queries| VoteModel
    Probability -->|Queries| SettingModel
    Probability -->|Queries| NoteModel
    XMLParser -->|Creates| RecordModel
    XMLParser -->|Creates| NoteModel
    XMLParser -->|Creates| VoteModel
    XMLParser -->|Queries| UserModel
    XMLExporter -->|Queries| RecordModel
    XMLExporter -->|Queries| NoteModel
    XMLExporter -->|Calls| Probability
    SeedData -->|Creates| SettingModel

    %% Data Access to Database
    UserModel -->|Reads/Writes| SQLite
    RecordModel -->|Reads/Writes| SQLite
    NoteModel -->|Reads/Writes| SQLite
    VoteModel -->|Reads/Writes| SQLite
    ReviewModel -->|Reads/Writes| SQLite
    SettingModel -->|Reads/Writes| SQLite

    %% Model Relationships
    UserModel -.->|1:N| VoteModel
    UserModel -.->|1:N| ReviewModel
    RecordModel -.->|1:N| NoteModel
    NoteModel -.->|1:N| VoteModel
    NoteModel -.->|1:N| ReviewModel

    style Presentation fill:#e1f5ff
    style Routing fill:#ffe1f5
    style BusinessLogic fill:#e1ffe1
    style DataAccess fill:#f5e1ff
    style Core fill:#fff4e1
    style Database fill:#ffe1e1
```

## Layer Descriptions

### Presentation Layer
**Components**: Templates, JavaScript, CSS

**Responsibilities**:
- Render HTML using Jinja2 templates
- Handle user interactions via JavaScript
- Style UI components with CSS

**Interactions**:
- Templates render data from route handlers
- JavaScript makes AJAX calls to voting endpoints
- Templates extend `base.html` for consistent layout

### Routing Layer (Blueprints)
**Components**: auth.py, routes/main.py, routes/voting.py, routes/filters.py, routes/admin.py

**Responsibilities**:
- Handle HTTP requests and responses
- Validate input data
- Coordinate between business logic and data access
- Return HTML templates or JSON responses

**Key Interactions**:
- All routes use `@login_required` decorator from auth.py
- Admin routes use `@admin_required` decorator
- Routes call utility functions for business logic
- Routes query models for data access

### Business Logic Layer
**Components**: utils/probability.py, utils/xml_parser.py, utils/xml_exporter.py, utils/seed_data.py

**Responsibilities**:
- Calculate vote distributions and consensus
- Parse and export XML files
- Implement core voting algorithms
- Seed default settings

**Key Interactions**:
- `probability.py` queries Vote and Setting models
- `xml_parser.py` creates Record, Note, and Vote models
- `xml_exporter.py` queries models and calls probability functions
- All utilities depend on models for data access

### Data Access Layer
**Components**: models.py with all model classes

**Responsibilities**:
- Define database schema via SQLAlchemy ORM
- Provide object-relational mapping
- Handle database relationships and constraints
- Abstract database operations

**Key Interactions**:
- Models map to SQLite database tables
- Relationships defined via SQLAlchemy relationships
- Foreign keys enforce referential integrity
- Cascade deletes maintain data consistency

### Core Application
**Components**: app.py, config.py

**Responsibilities**:
- Application factory pattern
- Configuration management
- Blueprint registration
- Database initialization

**Key Interactions**:
- Registers all blueprints
- Initializes SQLAlchemy database connection
- Configures Flask app settings
- Sets up WAL mode for SQLite

## Dependency Flow

### Request Flow (Top to Bottom)
1. **Browser** → HTTP request
2. **Flask App** → Routes to blueprint
3. **Blueprint** → Uses decorators from auth.py
4. **Blueprint** → Calls utility functions
5. **Utility** → Queries models
6. **Model** → Executes SQL queries
7. **Database** → Returns data
8. **Response** → Flows back up through layers

### Data Flow (Bottom to Top)
1. **Database** → Raw data
2. **Models** → Python objects
3. **Utilities** → Processed data structures
4. **Blueprints** → Formatted responses (JSON/HTML)
5. **Templates** → Rendered HTML
6. **Browser** → Displayed to user

## Key Interaction Patterns

### Authentication Pattern
```
Request → Blueprint → @login_required → auth.py → Check Session → User Model → Database
```

### Voting Pattern
```
Request → voting.py → Validate → Note Model → Vote Model → Database
         ↓
    Calculate Distribution → probability.py → Vote Model → Setting Model → Database
         ↓
    Return JSON → Browser → Update UI
```

### XML Import Pattern
```
Upload → admin.py → xml_parser.py → Record Model → Note Model → Vote Model → Database
```

### XML Export Pattern
```
Request → admin.py → xml_exporter.py → Record Model → Note Model → probability.py → Generate XML
```

## Decorator Usage

### @login_required
- **Defined in**: `auth.py`
- **Used by**: All route handlers except login/logout
- **Function**: Checks session for username, redirects if not logged in
- **Dependencies**: Session management, User model

### @admin_required
- **Defined in**: `auth.py`
- **Used by**: All admin routes
- **Function**: Checks session and User.is_admin flag
- **Dependencies**: @login_required, User model

## Utility Function Dependencies

### utils/probability.py
**Dependencies**:
- `models.Vote` - Query votes for distribution calculation
- `models.Setting` - Read contentious threshold and min votes
- `models.Note` - Count identical notes

**Used by**:
- `routes/main.py` - Display vote distributions
- `routes/voting.py` - Calculate after vote submission
- `routes/filters.py` - Filter contentious/unknown notes
- `routes/admin.py` - Dashboard statistics
- `utils/xml_exporter.py` - Export consensus classifications

### utils/xml_parser.py
**Dependencies**:
- `models.Record` - Create records
- `models.Note` - Create notes
- `models.Vote` - Optionally create initial votes
- `models.User` - Get admin user for initial votes

**Used by**:
- `routes/admin.py` - XML import functionality

### utils/xml_exporter.py
**Dependencies**:
- `models.Record` - Query all records
- `models.Note` - Query notes per record
- `utils/probability.py` - Calculate distributions for export

**Used by**:
- `routes/admin.py` - XML export functionality

## Model Relationships

### User Model
- **Has many**: Votes, Reviews, Source Records (via source_user_id)
- **Used by**: All routes for authentication, admin routes for statistics

### Record Model
- **Has many**: Notes
- **Belongs to**: User (optional, via source_user_id)
- **Used by**: Main routes, admin routes, XML import/export

### Note Model
- **Belongs to**: Record
- **Has many**: Votes, Reviews
- **Used by**: All routes that display or process notes

### Vote Model
- **Belongs to**: Note, User
- **Used by**: Voting routes, probability calculations, filters

### Setting Model
- **Standalone**: No relationships
- **Used by**: Probability calculations, admin settings

## Circular Dependencies Avoided

The architecture avoids circular dependencies through:
- **Unidirectional flow**: Presentation → Routing → Business Logic → Data Access → Database
- **Dependency injection**: Blueprints receive models/utilities, not vice versa
- **Separation of concerns**: Each layer has distinct responsibilities

## Testing Implications

**Unit Testing**:
- Test utilities independently with mock models
- Test models independently with test database
- Test routes with mock utilities

**Integration Testing**:
- Test full request flow through all layers
- Test database operations with real SQLite
- Test authentication decorators with session mocks
