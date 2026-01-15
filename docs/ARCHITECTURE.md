# Architecture Documentation

Complete architectural documentation for the Classification Vote Web App.

## Overview

This Flask web application enables collaborative multi-user voting on note classifications in manuscript records. The system calculates consensus from votes, detects contentious classifications, and provides admin tools for data management.

## Architecture Diagrams

### 1. [System Architecture Overview](architecture/01-system-architecture.md)
High-level view of all system components and their relationships, showing how data flows from the client browser through the Flask application to the database.

**Key Topics**:
- Client layer (Browser, Bootstrap, JavaScript)
- Flask application layer (app factory, session management)
- Routing layer (blueprints)
- Business logic layer (utilities)
- Data access layer (SQLAlchemy models)
- Persistence layer (SQLite database)

### 2. [Database Schema (ER Diagram)](architecture/02-database-schema.md)
Entity-relationship diagram showing all database tables, their fields, relationships, and constraints.

**Key Topics**:
- Entity descriptions (User, Record, Note, Vote, Review, Setting)
- Relationships and foreign keys
- Unique constraints and indexes
- Cascade delete behavior
- Common query patterns

### 3. [Request Flow Diagram](architecture/03-request-flow.md)
Sequence diagram tracing a vote submission from browser click through the entire system to database persistence and UI update.

**Key Topics**:
- Single vote submission flow
- Bulk voting flow (vote-identical)
- Error handling flow
- Authentication checks
- Consensus calculation process
- UI update strategy

### 4. [Component Interaction Diagram](architecture/04-component-interaction.md)
Shows how Flask blueprints, utilities, and models interact across different layers of the application.

**Key Topics**:
- Layer descriptions (Presentation, Routing, Business Logic, Data Access)
- Dependency flow
- Decorator usage patterns
- Utility function dependencies
- Model relationships
- Circular dependency avoidance

### 5. [User Journey Diagram](architecture/05-user-journey.md)
End-to-end user workflows showing how users interact with the system from login through various voting and navigation scenarios.

**Key Topics**:
- Main user flows (login, voting, navigation)
- Detailed voting flow
- Navigation patterns (mouse, keyboard, quick jump, filters)
- Admin workflows (import, export, settings)
- Error scenarios
- Decision points

## Quick Reference

### Technology Stack
- **Backend**: Flask 2.3.3, SQLAlchemy 3.0.5, Flask-Migrate 4.0.5
- **Database**: SQLite with WAL mode
- **Frontend**: Bootstrap 5, JavaScript (ES6), Jinja2 templates
- **Authentication**: Session-based (username-only, no passwords)

### Key Files
- `app.py` - Application factory
- `models.py` - Database models
- `auth.py` - Authentication system
- `routes/` - Route blueprints (main, voting, filters, admin)
- `utils/` - Business logic (probability, xml_parser, xml_exporter)
- `templates/` - Jinja2 HTML templates
- `static/` - JavaScript and CSS files

### Classification Types
- **W** (Work) - Intellectual content
- **O** (Object) - Physical description
- **A** (Administrative) - Cataloging/processing
- **OW, AW, AO** - Hybrid combinations
- **?** (Unknown) - Unclear classification

### Key Features
- Multi-user voting with consensus calculation
- Contentious note detection (configurable threshold)
- Bulk voting for identical notes
- XML import/export
- Admin dashboard and settings
- Filter views (unknown, pending review, contentious)
- Keyboard navigation
- Vote privacy (hidden by default)

## Architecture Principles

### Separation of Concerns
- **Presentation**: Templates and static files
- **Routing**: Blueprints handle HTTP requests
- **Business Logic**: Utilities contain core algorithms
- **Data Access**: Models abstract database operations
- **Persistence**: SQLite database

### Security Model
- Username-only authentication (trusted team environment)
- Session-based with 7-day persistence
- Admin auto-grant for "Admin" username
- Input validation on all endpoints
- SQL injection protection via ORM

### Performance Considerations
- Eager loading with `joinedload()` to avoid N+1 queries
- WAL mode for better SQLite concurrency
- AJAX for asynchronous updates
- Indexed foreign keys for fast lookups
- Single transaction for bulk operations

### Scalability Notes
- SQLite suitable for small-to-medium teams
- WAL mode improves concurrent reads
- Can migrate to PostgreSQL for better multi-user performance
- Caching opportunities for vote distributions

## Common Patterns

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

## Database Schema Summary

### Tables
- **users** - User accounts (username, is_admin)
- **records** - Manuscript records (bib_id, title, source metadata)
- **notes** - Individual notes within records (text, note_index)
- **votes** - User classifications (note_id, user_id, classification)
- **reviews** - Approval status (note_id, user_id, approval)
- **settings** - Configurable system settings (key, value)

### Key Constraints
- One vote per user per note (composite unique)
- One review per user per note (composite unique)
- Unique note positions within records (composite unique)
- Foreign keys with cascade deletes

## Development Guidelines

### Adding New Features
1. **Routes**: Add to appropriate blueprint in `routes/`
2. **Models**: Update `models.py` and create migration
3. **UI**: Modify templates in `templates/`
4. **Client Logic**: Update `static/js/app.js`

### Testing Considerations
- Unit test utilities independently with mocks
- Integration test full request flows
- Test authentication decorators with session mocks
- Test database operations with test SQLite database

### Migration Strategy
- Use Flask-Migrate for schema changes
- Test migrations on sample data
- Document breaking changes
- Consider data migration scripts for complex changes

## Related Documentation

- [README.md](../README.md) - Setup and usage instructions
- [CLAUDE.md](../CLAUDE.md) - Development guide and architecture overview
- [setup.md](../setup.md) - Environment setup instructions

## Diagram Conventions

All diagrams use Mermaid syntax for compatibility with:
- GitHub/GitLab markdown rendering
- Documentation generators
- Version control systems

Diagrams are organized by:
- **System level** (architecture overview)
- **Data level** (database schema)
- **Process level** (request flows, user journeys)
- **Component level** (interactions)
