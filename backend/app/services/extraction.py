"""Rule-based extraction of medicine name, dosage, frequency, duration and instructions from OCR text."""
import re
from dataclasses import dataclass

NOT_DETECTED = "Not detected"

DOSAGE_RE = re.compile(
    r"(\d+(?:\.\d+)?\s?(?:mg|mcg|µg|ug|g|ml|iu|units?|%)(?:\s?/\s?\d+(?:\.\d+)?\s?(?:ml|mg|g))?)(?![a-z])",
    re.IGNORECASE)

_FREQ_ABBR = {"OD": "Once daily", "QD": "Once daily", "BD": "Twice daily", "BID": "Twice daily",
              "TDS": "Three times daily", "TID": "Three times daily", "QID": "Four times daily",
              "QDS": "Four times daily", "HS": "At bedtime", "SOS": "As needed", "PRN": "As needed"}
_FREQ_PATTERNS = [
    (re.compile(r"\b(\d)\s?-\s?(\d)\s?-\s?(\d)(?:\s?-\s?(\d))?\b"), lambda m: m.group(0).replace(" ", "")),
    (re.compile(r"\b(once|twice|thrice)\s+(?:a\s+|per\s+)?(?:day|daily)\b", re.I), lambda m: m.group(0).capitalize()),
    (re.compile(r"\b(\d)\s*(?:times|x)\s*(?:a|per)?\s*(?:day|daily)\b", re.I),
     lambda m: f"{m.group(1)} times daily"),
    (re.compile(r"\bevery\s+\d+\s*(?:hours?|hrs?|h)\b", re.I), lambda m: m.group(0).capitalize()),
    (re.compile(r"\b(OD|QD|BD|BID|TDS|TID|QID|QDS|HS|SOS|PRN)\b", re.I), lambda m: _FREQ_ABBR[m.group(1).upper()]),
    (re.compile(r"\bdaily\b", re.I), lambda m: "Once daily"),
]
DURATION_RE = re.compile(r"\b(?:for|x)?\s*(\d+)\s*(days?|weeks?|months?)\b", re.I)
_INSTRUCTION_RE = re.compile(
    r"\b(after (?:food|meals?)|before (?:food|meals?)|with (?:food|water|milk)|empty stomach|at bedtime|"
    r"do not crush|avoid alcohol)\b", re.I)
_FORM_PREFIX_RE = re.compile(
    r"^\s*(?:\d+\s*[.)]\s*)?(?:tab(?:let)?s?|cap(?:sule)?s?|syp|syrup|inj(?:ection)?|oint(?:ment)?|drops?|cream|gel)\b\.?\s*",
    re.I)
_NUMBERING_RE = re.compile(r"^\s*\d+\s*[.)]\s+")


@dataclass
class ExtractedMedicine:
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str | None

    @property
    def needs_review(self) -> bool:
        return NOT_DETECTED in (self.medicine_name, self.dosage, self.frequency, self.duration)


def _find_frequency(text: str):
    for pattern, normalise in _FREQ_PATTERNS:
        m = pattern.search(text)
        if m:
            return normalise(m), m
    return None, None


def _find_duration(text: str):
    m = DURATION_RE.search(text)
    if not m:
        return None, None
    n, unit = int(m.group(1)), m.group(2).lower().rstrip("s")
    return f"{n} {unit}{'' if n == 1 else 's'}", m


def parse_line(line: str) -> ExtractedMedicine | None:
    """Return a medicine if the line looks like a prescription line, else None."""
    text = " ".join(line.split())
    dosage_m = DOSAGE_RE.search(text)
    has_prefix = bool(_FORM_PREFIX_RE.match(text))
    if not dosage_m and not has_prefix:
        return None

    freq, freq_m = _find_frequency(text)
    dur, dur_m = _find_duration(text)
    # a duration like "5 days" must not be confused with a dosage unit; dosage regex has no day units.

    body = _FORM_PREFIX_RE.sub("", text) if has_prefix else _NUMBERING_RE.sub("", text)
    cut_points = [m.start() for m in (DOSAGE_RE.search(body), _find_frequency(body)[1], _find_duration(body)[1]) if m]
    name = body[: min(cut_points)] if cut_points else body
    name = name.strip(" -–:,.;()")
    if not re.search(r"[A-Za-z]{2,}", name):
        name = ""

    instr = _INSTRUCTION_RE.findall(text)
    instructions = "; ".join(dict.fromkeys(i.capitalize() for i in instr)) or None
    return ExtractedMedicine(
        medicine_name=name or NOT_DETECTED,
        dosage=re.sub(r"\s+", " ", dosage_m.group(1)).strip() if dosage_m else NOT_DETECTED,
        frequency=freq or NOT_DETECTED,
        duration=dur or NOT_DETECTED,
        instructions=instructions)


def extract_medicines(text: str) -> list[ExtractedMedicine]:
    meds = []
    for line in text.splitlines():
        if line.strip():
            med = parse_line(line)
            if med:
                meds.append(med)
    return meds
