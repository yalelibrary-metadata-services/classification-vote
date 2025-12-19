from models import db, Setting


def seed_default_settings():
    """Initialize default settings in the database"""
    defaults = [
        {
            'key': 'contentious_threshold',
            'value': '0.70',
            'description': 'Minimum consensus probability to avoid contentious marking (0-1). '
                          'Notes with consensus below this threshold will be marked as contentious.'
        },
        {
            'key': 'min_votes_contentious',
            'value': '3',
            'description': 'Minimum number of votes required before marking a note as contentious. '
                          'Notes with fewer votes will not be marked as contentious.'
        }
    ]

    for default in defaults:
        existing = Setting.query.filter_by(key=default['key']).first()
        if not existing:
            setting = Setting(**default)
            db.session.add(setting)
            print(f"Created setting: {default['key']} = {default['value']}")
        else:
            print(f"Setting already exists: {default['key']} = {existing.value}")

    db.session.commit()
    print("Default settings seeded successfully")


if __name__ == '__main__':
    # Run standalone for testing
    from app import create_app
    app = create_app()

    with app.app_context():
        seed_default_settings()
