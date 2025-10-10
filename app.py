from flask import Flask, render_template, request, jsonify, redirect, url_for
import xml.etree.ElementTree as ET
import os
from datetime import datetime

app = Flask(__name__)

XML_FILE = 'data.xml'

def load_xml_data():
    if not os.path.exists(XML_FILE):
        return None
    tree = ET.parse(XML_FILE)
    return tree

def save_xml_data(tree):
    tree.write(XML_FILE, encoding='utf-8', xml_declaration=True)

def get_records():
    tree = load_xml_data()
    if tree is None:
        return []
    
    records = []
    for record in tree.findall('record'):
        bib = record.get('bib')
        title = record.find('title')
        title_text = title.text if title is not None else 'No title'
        
        notes = []
        for note in record.findall('note'):
            note_data = {
                'text': note.text or '',
                'type': note.get('type', ''),
                'reviewer': note.get('reviewer', ''),
                'review': note.get('review', ''),
                'index': list(record).index(note)
            }
            notes.append(note_data)
        
        records.append({
            'bib': bib,
            'title': title_text,
            'notes': notes
        })
    
    return records

@app.route('/')
def index():
    records = get_records()
    return render_template('index.html', records=records)

@app.route('/record/<bib_id>')
def record_detail(bib_id):
    records = get_records()
    record = next((r for r in records if r['bib'] == bib_id), None)
    if not record:
        return "Record not found", 404
    
    # Find current record index and navigation info
    current_index = next((i for i, r in enumerate(records) if r['bib'] == bib_id), None)
    prev_record = records[current_index - 1] if current_index > 0 else None
    next_record = records[current_index + 1] if current_index < len(records) - 1 else None
    
    return render_template('record.html', 
                         record=record, 
                         prev_record=prev_record, 
                         next_record=next_record,
                         current_index=current_index,
                         total_records=len(records))

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    bib_id = data.get('bib_id')
    note_index = int(data.get('note_index'))
    classification = data.get('classification')
    
    if classification not in ['w', 'o', 'a', 'ow', 'aw', 'ao', '?']:
        return jsonify({'error': 'Invalid classification'}), 400
    
    tree = load_xml_data()
    if tree is None:
        return jsonify({'error': 'No XML data found'}), 404
    
    record = tree.find(f"record[@bib='{bib_id}']")
    if record is None:
        return jsonify({'error': 'Record not found'}), 404
    
    notes = record.findall('note')
    if note_index >= len(notes):
        return jsonify({'error': 'Note not found'}), 404
    
    note = notes[note_index]
    note.set('type', classification)
    
    save_xml_data(tree)
    
    return jsonify({'success': True, 'new_type': classification})

@app.route('/review', methods=['POST'])
def review():
    data = request.json
    bib_id = data.get('bib_id')
    note_index = int(data.get('note_index'))
    reviewer = data.get('reviewer', '').strip()
    review = data.get('review')
    
    if review not in ['y', 'n', '?']:
        return jsonify({'error': 'Invalid review status'}), 400
    
    if not reviewer:
        return jsonify({'error': 'Reviewer initials required'}), 400
    
    tree = load_xml_data()
    if tree is None:
        return jsonify({'error': 'No XML data found'}), 404
    
    record = tree.find(f"record[@bib='{bib_id}']")
    if record is None:
        return jsonify({'error': 'Record not found'}), 404
    
    notes = record.findall('note')
    if note_index >= len(notes):
        return jsonify({'error': 'Note not found'}), 404
    
    note = notes[note_index]
    note.set('reviewer', reviewer)
    note.set('review', review)
    
    save_xml_data(tree)
    
    return jsonify({
        'success': True, 
        'reviewer': reviewer, 
        'review': review
    })

@app.route('/unknown')
def unknown_records():
    records = get_records()
    unknown_records = []
    
    for record in records:
        unknown_notes = []
        for note in record['notes']:
            if note['type'] == '?':
                unknown_notes.append(note)
        
        if unknown_notes:
            unknown_records.append({
                'bib': record['bib'],
                'title': record['title'],
                'unknown_notes': unknown_notes,
                'total_notes': len(record['notes']),
                'unknown_count': len(unknown_notes)
            })
    
    return render_template('unknown.html', 
                         unknown_records=unknown_records, 
                         total_unknown_records=len(unknown_records))

@app.route('/pending-review')
def pending_review():
    records = get_records()
    pending_records = []
    
    for record in records:
        pending_notes = []
        for note in record['notes']:
            # Notes that have classifications but no review or are marked as needing review
            if note['type'] and note['type'] != '?' and (not note['review'] or note['review'] == '?'):
                pending_notes.append(note)
        
        if pending_notes:
            pending_records.append({
                'bib': record['bib'],
                'title': record['title'],
                'pending_notes': pending_notes,
                'total_notes': len(record['notes']),
                'pending_count': len(pending_notes)
            })
    
    return render_template('pending_review.html', 
                         pending_records=pending_records, 
                         total_pending_records=len(pending_records))

def find_next_record_with_condition(records, current_bib, condition_func):
    """Helper function to find next record matching a condition after current record"""
    current_index = next((i for i, r in enumerate(records) if r['bib'] == current_bib), -1)
    
    if current_index == -1:
        return None
    
    # Search from current position + 1 to end
    for i in range(current_index + 1, len(records)):
        if condition_func(records[i]):
            return records[i]
    
    # Search from beginning to current position (wrap around)
    for i in range(0, current_index):
        if condition_func(records[i]):
            return records[i]
    
    return None

def has_blank_notes(record):
    """Check if record has any blank/unclassified notes"""
    for note in record['notes']:
        if not note['type'] or note['type'].strip() == '':
            return True
    return False

def has_unknown_notes(record):
    """Check if record has any unknown (?) notes"""
    for note in record['notes']:
        if note['type'] == '?':
            return True
    return False

def has_pending_review_notes(record):
    """Check if record has any notes pending review"""
    for note in record['notes']:
        if note['type'] and note['type'] != '?' and (not note['review'] or note['review'] == '?'):
            return True
    return False

@app.route('/start-unclassified')
def start_unclassified():
    records = get_records()
    
    # Find first record with blank (empty) classifications
    for record in records:
        if has_blank_notes(record):
            return redirect(url_for('record_detail', bib_id=record['bib']))
    
    # If no records with blank classifications found, go to first record
    if records:
        return redirect(url_for('record_detail', bib_id=records[0]['bib']))
    
    # If no records at all, go to home page
    return redirect(url_for('index'))

@app.route('/next-unclassified/<current_bib>')
def next_unclassified(current_bib):
    records = get_records()
    next_record = find_next_record_with_condition(records, current_bib, has_blank_notes)
    
    if next_record:
        return redirect(url_for('record_detail', bib_id=next_record['bib']))
    else:
        # No more unclassified records, stay on current record
        return redirect(url_for('record_detail', bib_id=current_bib))

@app.route('/next-unknown/<current_bib>')
def next_unknown(current_bib):
    records = get_records()
    next_record = find_next_record_with_condition(records, current_bib, has_unknown_notes)
    
    if next_record:
        return redirect(url_for('record_detail', bib_id=next_record['bib']))
    else:
        # No more unknown records, stay on current record
        return redirect(url_for('record_detail', bib_id=current_bib))

@app.route('/next-pending-review/<current_bib>')
def next_pending_review(current_bib):
    records = get_records()
    next_record = find_next_record_with_condition(records, current_bib, has_pending_review_notes)
    
    if next_record:
        return redirect(url_for('record_detail', bib_id=next_record['bib']))
    else:
        # No more pending review records, stay on current record
        return redirect(url_for('record_detail', bib_id=current_bib))

if __name__ == '__main__':
    app.run(debug=True)