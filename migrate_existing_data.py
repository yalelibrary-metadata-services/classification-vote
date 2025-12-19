"""
One-time migration script to import existing data.xml into database.

This script:
1. Creates all database tables
2. Seeds default settings
3. Creates an admin user
4. Imports the existing data.xml file with initial votes

Usage:
    python migrate_existing_data.py
"""

from app import create_app
from models import db, User
from utils.xml_parser import import_xml_file
from utils.seed_data import seed_default_settings
import os


def migrate():
    """Run the migration"""
    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("Classification Vote System - Data Migration")
        print("=" * 60)

        # Create tables if they don't exist
        print("\n1. Creating database tables...")
        db.create_all()
        print("   ✓ Tables created successfully")

        # Seed default settings
        print("\n2. Seeding default settings...")
        seed_default_settings()

        # Create admin user
        print("\n3. Creating admin user...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print(f"   ✓ Created admin user (ID: {admin.id})")
        else:
            print(f"   ℹ Admin user already exists (ID: {admin.id})")

        # Import existing XML
        xml_path = os.path.join(os.path.dirname(__file__), 'data.xml')

        if not os.path.exists(xml_path):
            print(f"\n   ✗ ERROR: {xml_path} not found")
            print("   Please ensure data.xml exists in the project directory")
            return

        print(f"\n4. Importing {xml_path}...")
        print("   This may take a few minutes for 16,000+ notes...")
        print("   Creating initial votes from existing classifications...")

        # Import with admin as initial voter
        stats = import_xml_file(xml_path, admin_user_id=admin.id)

        print("\n" + "=" * 60)
        print("Migration Complete!")
        print("=" * 60)
        print(f"Records created: {stats['records_created']}")
        print(f"Notes created: {stats['notes_created']}")
        print(f"Initial votes created: {stats['votes_created']}")

        if stats['errors']:
            print(f"\nWarnings/Errors ({len(stats['errors'])}):")
            for error in stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(stats['errors']) > 10:
                print(f"  ... and {len(stats['errors']) - 10} more")

        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python app.py")
        print("3. Open browser to: http://localhost:5000")
        print("4. Login with username: admin (or any username)")
        print("\nYour original data.xml has not been modified.")
        print("=" * 60)


if __name__ == '__main__':
    migrate()
