import pytest
from app.services.extraction import NOT_DETECTED, extract_medicines, parse_line


@pytest.mark.parametrize("line,name,dosage,freq,dur", [
    ("Tab. Paracetamol 500 mg BD x 5 days", "Paracetamol", "500 mg", "Twice daily", "5 days"),
    ("1. Amoxicillin 250mg 1-0-1 for 7 days", "Amoxicillin", "250mg", "1-0-1", "7 days"),
    ("Cap Omeprazole 20 mg once daily for 2 weeks", "Omeprazole", "20 mg", "Once daily", "2 weeks"),
    ("Syp. Cetirizine 5 ml TDS 3 days", "Cetirizine", "5 ml", "Three times daily", "3 days"),
    ("Metformin 500 mg every 12 hours for 1 month", "Metformin", "500 mg", "Every 12 hours", "1 month"),
    ("Azithromycin 500mg 2 times a day for 1 day", "Azithromycin", "500mg", "2 times daily", "1 day"),
])
def test_parse_complete_lines(line, name, dosage, freq, dur):
    m = parse_line(line)
    assert (m.medicine_name, m.dosage, m.frequency, m.duration) == (name, dosage, freq, dur)
    assert not m.needs_review


def test_dosage_preserved_exactly():
    assert parse_line("Tab Levothyroxine 12.5 mcg OD 30 days").dosage == "12.5 mcg"
    assert parse_line("Syp Amoxicillin 250 mg/5 ml BD 5 days").dosage == "250 mg/5 ml"


def test_instructions_captured():
    m = parse_line("Tab Ibuprofen 400 mg TDS 3 days after food")
    assert m.instructions == "After food"


def test_missing_fields_flagged_for_review():
    m = parse_line("Tab Paracetamol 500 mg")
    assert m.frequency == NOT_DETECTED and m.duration == NOT_DETECTED and m.needs_review
    m = parse_line("Tab Paracetamol BD 5 days")
    assert m.dosage == NOT_DETECTED and m.needs_review


def test_non_medicine_lines_ignored():
    text = "Dr. Mehta MBBS\nPatient: Asha Rao  Age 31\nDate: 20-10-2026\nRx\nTab Paracetamol 500 mg BD 5 days\nSign"
    meds = extract_medicines(text)
    assert [m.medicine_name for m in meds] == ["Paracetamol"]


def test_multiple_medicines_and_empty_text():
    text = "Tab Paracetamol 500 mg BD 5 days\nCap Omeprazole 20 mg OD 14 days"
    assert len(extract_medicines(text)) == 2
    assert extract_medicines("") == [] and extract_medicines("random words only") == []
