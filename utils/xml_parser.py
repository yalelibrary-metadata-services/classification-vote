import xml.etree.ElementTree as ET
from models import db, Record, Note, Vote

def import_xml_file(xml_path, admin_user_id=None):
    """
    Import XML file into database.

    Args:
        xml_path: Path to XML file
        admin_user_id: If provided, create initial votes from existing type attributes

    Returns:
        dict with keys:
            - records_created: Number of records created
            - notes_created: Number of notes created
            - votes_created: Number of initial votes created
            - errors: List of error messages
    """
    stats = {
        'records_created': 0,
        'notes_created': 0,
        'votes_created': 0,
        'errors': []
    }

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for record_elem in root.findall('record'):
            try:
                bib_id = record_elem.get('bib')
                if not bib_id:
                    stats['errors'].append('Record without bib ID skipped')
                    continue

                # Check if record already exists
                existing_record = Record.query.filter_by(bib_id=bib_id).first()
                if existing_record:
                    stats['errors'].append(f'Record {bib_id} already exists, skipped')
                    continue

                # Get title
                title_elem = record_elem.find('title')
                title_text = title_elem.text if title_elem is not None and title_elem.text else 'No title'

                # Create record
                record = Record(bib_id=bib_id, title=title_text)
                db.session.add(record)
                db.session.flush()  # Get record.id

                stats['records_created'] += 1

                # Process notes
                note_index = 0
                for note_elem in record_elem.findall('note'):
                    note_text = note_elem.text or ''
                    note_type = note_elem.get('type', '')

                    # Create note
                    note = Note(
                        record_id=record.id,
                        note_index=note_index,
                        text=note_text
                    )
                    db.session.add(note)
                    db.session.flush()  # Get note.id

                    stats['notes_created'] += 1

                    # Create initial vote if type exists and admin_user_id provided
                    if note_type and note_type.strip() and admin_user_id:
                        # Validate classification type
                        if note_type in ['w', 'o', 'a', 'ow', 'aw', 'ao', '?']:
                            vote = Vote(
                                note_id=note.id,
                                user_id=admin_user_id,
                                classification=note_type
                            )
                            db.session.add(vote)
                            stats['votes_created'] += 1

                    note_index += 1

            except Exception as e:
                stats['errors'].append(f'Error processing record {bib_id}: {str(e)}')
                continue

        # Commit all changes
        db.session.commit()

    except ET.ParseError as e:
        db.session.rollback()
        stats['errors'].append(f'XML parsing error: {str(e)}')
    except Exception as e:
        db.session.rollback()
        stats['errors'].append(f'Import failed: {str(e)}')

    return stats


def clear_database():
    """
    Clear all data from database (use with caution!).
    Does not delete users or settings.
    """
    from models import Review
    try:
        Vote.query.delete()
        Review.query.delete()
        Note.query.delete()
        Record.query.delete()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f'Failed to clear database: {str(e)}')
