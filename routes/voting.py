from flask import Blueprint, request, jsonify, session
from datetime import datetime
from models import db, Record, Note, Vote
from auth import login_required
from utils.probability import calculate_vote_distribution, get_identical_note_ids

voting_bp = Blueprint('voting', __name__)


@voting_bp.route('/vote', methods=['POST'])
@login_required
def vote():
    """
    Handle classification vote submission.
    Allows users to create or update their vote for a note.
    """
    data = request.json
    bib_id = data.get('bib_id')
    note_index = data.get('note_index')
    classification = data.get('classification')

    # Validate classification
    if classification not in ['w', 'o', 'a', 'ow', 'aw', 'ao', '?']:
        return jsonify({'error': 'Invalid classification'}), 400

    # Validate note_index
    try:
        note_index = int(note_index)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid note index'}), 400

    # Get record by bib_id
    record = Record.query.filter_by(bib_id=bib_id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    # Get note by record_id and note_index
    note = Note.query.filter_by(record_id=record.id, note_index=note_index).first()
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    user_id = session.get('user_id')

    # Check if user already voted - update or create
    existing_vote = Vote.query.filter_by(note_id=note.id, user_id=user_id).first()

    if existing_vote:
        # Update existing vote
        existing_vote.classification = classification
        existing_vote.voted_at = datetime.utcnow()
    else:
        # Create new vote
        new_vote = Vote(
            note_id=note.id,
            user_id=user_id,
            classification=classification
        )
        db.session.add(new_vote)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    # Calculate new distribution
    distribution = calculate_vote_distribution(note.id)

    # Get voters grouped by classification
    votes = Vote.query.filter_by(note_id=note.id).all()
    voters = {}
    for vote in votes:
        if vote.classification not in voters:
            voters[vote.classification] = []
        voters[vote.classification].append(vote.user.username)

    return jsonify({
        'success': True,
        'classification': classification,
        'distribution': distribution,
        'consensus': distribution['consensus'],
        'consensus_probability': distribution['consensus_probability'],
        'is_contentious': distribution['is_contentious'],
        'voters': voters
    })


@voting_bp.route('/vote-identical', methods=['POST'])
@login_required
def vote_identical():
    """
    Handle bulk classification vote for all identical notes.
    Applies the same classification to all notes with matching text.
    """
    data = request.json
    note_text = data.get('note_text')
    classification = data.get('classification')

    # Validate classification
    if classification not in ['w', 'o', 'a', 'ow', 'aw', 'ao', '?']:
        return jsonify({'error': 'Invalid classification'}), 400

    if not note_text:
        return jsonify({'error': 'Note text required'}), 400

    user_id = session.get('user_id')

    # Get all notes with matching text
    note_ids = get_identical_note_ids(note_text)

    if not note_ids:
        return jsonify({'error': 'No matching notes found'}), 404

    votes_created = 0
    votes_updated = 0

    try:
        for note_id in note_ids:
            # Check if user already voted - update or create
            existing_vote = Vote.query.filter_by(note_id=note_id, user_id=user_id).first()

            if existing_vote:
                existing_vote.classification = classification
                existing_vote.voted_at = datetime.utcnow()
                votes_updated += 1
            else:
                new_vote = Vote(
                    note_id=note_id,
                    user_id=user_id,
                    classification=classification
                )
                db.session.add(new_vote)
                votes_created += 1

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'classification': classification,
        'total_notes': len(note_ids),
        'votes_created': votes_created,
        'votes_updated': votes_updated
    })


