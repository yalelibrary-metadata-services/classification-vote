from flask import Blueprint, render_template, session
from models import Record, Note, Vote
from auth import login_required
from utils.probability import calculate_vote_distribution

filters_bp = Blueprint('filters', __name__)


@filters_bp.route('/unknown')
@login_required
def unknown_records():
    """Show records with notes where consensus is '?'"""

    unknown_records = []
    records = Record.query.order_by(Record.bib_id).all()

    for record in records:
        notes = Note.query.filter_by(record_id=record.id).order_by(Note.note_index).all()
        unknown_notes = []

        for note in notes:
            distribution = calculate_vote_distribution(note.id)
            if distribution['consensus'] == '?':
                unknown_notes.append({
                    'text': note.text[:150] + ('...' if len(note.text) > 150 else ''),
                    'text_full': note.text,
                    'index': note.note_index,
                    'distribution': distribution
                })

        if unknown_notes:
            unknown_records.append({
                'bib': record.bib_id,
                'title': record.title,
                'unknown_notes': unknown_notes,
                'total_notes': len(notes),
                'unknown_count': len(unknown_notes)
            })

    return render_template('unknown.html',
                         unknown_records=unknown_records,
                         total_unknown_records=len(unknown_records))


@filters_bp.route('/pending-review')
@login_required
def pending_review():
    """Show notes where current user hasn't voted yet"""
    user_id = session.get('user_id')

    pending_records = []
    records = Record.query.order_by(Record.bib_id).all()

    for record in records:
        notes = Note.query.filter_by(record_id=record.id).order_by(Note.note_index).all()
        pending_notes = []

        for note in notes:
            # User hasn't voted on this note yet
            user_vote = Vote.query.filter_by(note_id=note.id, user_id=user_id).first()

            if not user_vote:
                distribution = calculate_vote_distribution(note.id)
                pending_notes.append({
                    'text': note.text[:150] + ('...' if len(note.text) > 150 else ''),
                    'text_full': note.text,
                    'index': note.note_index,
                    'distribution': distribution
                })

        if pending_notes:
            pending_records.append({
                'bib': record.bib_id,
                'title': record.title,
                'pending_notes': pending_notes,
                'total_notes': len(notes),
                'pending_count': len(pending_notes)
            })

    return render_template('pending_review.html',
                         pending_records=pending_records,
                         total_pending_records=len(pending_records))


@filters_bp.route('/contentious')
@login_required
def contentious_records():
    """Show notes where consensus is below threshold with sufficient votes"""

    contentious_records = []
    records = Record.query.order_by(Record.bib_id).all()

    for record in records:
        notes = Note.query.filter_by(record_id=record.id).order_by(Note.note_index).all()
        contentious_notes = []

        for note in notes:
            distribution = calculate_vote_distribution(note.id)
            if distribution['is_contentious']:
                contentious_notes.append({
                    'text': note.text[:150] + ('...' if len(note.text) > 150 else ''),
                    'text_full': note.text,
                    'index': note.note_index,
                    'distribution': distribution
                })

        if contentious_notes:
            contentious_records.append({
                'bib': record.bib_id,
                'title': record.title,
                'contentious_notes': contentious_notes,
                'total_notes': len(notes),
                'contentious_count': len(contentious_notes)
            })

    return render_template('contentious.html',
                         contentious_records=contentious_records,
                         total_contentious_records=len(contentious_records))
