import xml.etree.ElementTree as ET
from xml.dom import minidom
from models import Record, Note
from utils.probability import calculate_vote_distribution


def export_to_xml(confidence_threshold=0.60, include_stats=True):
    """
    Export database to XML with consensus classifications.

    Args:
        confidence_threshold: Only include notes with probability >= threshold
        include_stats: Add vote_count and consensus_probability attributes

    Returns:
        XML string (bytes)
    """
    root = ET.Element('records')

    records = Record.query.order_by(Record.bib_id).all()

    for record in records:
        record_elem = ET.SubElement(root, 'record')
        record_elem.set('bib', record.bib_id)

        # Title
        title_elem = ET.SubElement(record_elem, 'title')
        title_elem.text = record.title

        # Notes
        notes = Note.query.filter_by(record_id=record.id)\
                          .order_by(Note.note_index).all()

        for note in notes:
            distribution = calculate_vote_distribution(note.id)

            # Skip notes below confidence threshold
            if distribution['consensus'] and \
               distribution['consensus_probability'] >= confidence_threshold:

                note_elem = ET.SubElement(record_elem, 'note')
                note_elem.text = note.text
                note_elem.set('type', distribution['consensus'])

                if include_stats:
                    note_elem.set('consensus_probability',
                                 f"{distribution['consensus_probability']:.2f}")
                    note_elem.set('vote_count', str(distribution['total']))

    # Pretty print XML
    xml_string = ET.tostring(root, encoding='utf-8')
    dom = minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')

    return pretty_xml


def export_to_file(filepath, confidence_threshold=0.60, include_stats=True):
    """
    Export to XML file.

    Args:
        filepath: Path to save XML file
        confidence_threshold: Only include notes with probability >= threshold
        include_stats: Add vote_count and consensus_probability attributes

    Returns:
        filepath
    """
    xml_content = export_to_xml(confidence_threshold, include_stats)

    with open(filepath, 'wb') as f:
        f.write(xml_content)

    return filepath
