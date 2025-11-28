"""Schedule parsing and storage utilities for Coach AI."""
from __future__ import annotations

import io
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# Optional PDF backends
try:
    import pdfplumber  # type: ignore
except Exception:
    pdfplumber = None  # type: ignore[assignment]

try:
    from PyPDF2 import PdfReader  # type: ignore
except Exception:
    PdfReader = None  # type: ignore[assignment]

EXPECTED_COLUMNS: List[str] = [
    "event_date",
    "start_time",
    "end_time",
    "event_type",
    "opponent",
    "location",
    "notes",
]

BAD_CHARS: Dict[str, str] = {
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\xa0": " ",
}

EVENT_PATTERN = re.compile(
    r"(?P<date>\d{2}/\d{2}/\d{4})\s+"
    r"(?P<time>\d{1,2}:\d{2}\s*(?:AM|PM))\s+"
    r"(?P<etype>Practice|Game)\s+"
    r"(?P<rest>.*?)(?=(\d{2}/\d{2}/\d{4})|\Z)",
    flags=re.IGNORECASE | re.DOTALL,
)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _sanitize_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    out = value
    for bad, good in BAD_CHARS.items():
        out = out.replace(bad, good)
    out = out.encode("ascii", "ignore").decode("ascii")
    return out.strip()


def _normalize_date(date_str: str) -> str:
    """Normalize dates to YYYY-MM-DD."""
    date_str = _sanitize_text(date_str)
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return date_str


def _normalize_time_12h(raw_time: str) -> str:
    """Return a 12-hour time like '7:00 PM'; fall back to raw on failure."""
    clean = _sanitize_text(raw_time).upper()
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M"):
        try:
            dt = datetime.strptime(clean, fmt)
            return dt.strftime("%I:%M %p").lstrip("0")
        except Exception:
            continue
    return raw_time


def _split_rest(rest: str, event_type: str) -> tuple[str, str, str]:
    """
    Split trailing details into opponent/location/notes.
    Heuristic tuned for the ND sample schedules; coaches can edit in UI.
    """
    words = rest.split()
    if not words:
        return "", "", ""

    et = event_type.lower()
    if et == "game":
        opponent_words = words[:2]
        location_words = words[2:4] if len(words) > 2 else []
        notes_words = words[4:] if len(words) > 4 else []
    else:
        opponent_words = words[:2]
        location_words = words[2:5] if len(words) > 2 else []
        notes_words = words[5:] if len(words) > 5 else []

    opponent = " ".join(opponent_words)
    location = " ".join(location_words)
    notes = " ".join(notes_words)
    return _sanitize_text(opponent), _sanitize_text(location), _sanitize_text(notes)


def _extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract all text from the PDF pages into a single string.
    Prefers pdfplumber; falls back to PyPDF2.
    """
    texts: List[str] = []
    if pdfplumber is not None:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt:
                        texts.append(txt)
        except Exception:
            texts = []
    if not texts and PdfReader is not None:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    texts.append(txt)
        except Exception:
            texts = []
    return "\n".join(texts)


def _extract_events_from_text(text: str) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    for match in EVENT_PATTERN.finditer(text):
        date_raw = match.group("date").strip()
        time_raw = match.group("time").strip()
        etype_raw = match.group("etype").strip()
        rest_raw = (match.group("rest") or "").strip()

        event_date = _normalize_date(date_raw)
        start_time = _normalize_time_12h(time_raw)
        event_type = "Game" if etype_raw.lower() == "game" else "Practice"
        opponent, location, notes = _split_rest(rest_raw, event_type)

        events.append(
            {
                "event_date": event_date,
                "start_time": start_time,
                "end_time": "",
                "event_type": event_type,
                "opponent": opponent,
                "location": location,
                "notes": notes,
            }
        )
    return events


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[EXPECTED_COLUMNS]
    for col in EXPECTED_COLUMNS:
        df[col] = df[col].map(_sanitize_text)
    return df


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def parse_pdf_schedule(file_bytes: bytes) -> pd.DataFrame:
    """
    Parse a PDF schedule into a DataFrame with EXPECTED_COLUMNS.
    Raises ValueError with helpful text if no events are found.
    """
    text = _extract_pdf_text(file_bytes)
    if not text.strip():
        raise ValueError("PDF contained no extractable text")

    # Optional debug text dump for troubleshooting
    try:
        dbg_path = Path(__file__).resolve().parent.parent / "debug_schedule_text.txt"
        dbg_path.write_text(_sanitize_text(text), encoding="utf-8")
    except Exception:
        pass

    events = _extract_events_from_text(_sanitize_text(text))
    if not events:
        preview = _sanitize_text(text.strip().replace("\n", " "))[:400]
        raise ValueError(
            "No schedule events could be parsed from this PDF. "
            f"First text: {preview}"
        )

    df = pd.DataFrame(events)
    df = _ensure_columns(df)
    return df


def load_team_schedule(team_id: str, data_path: Path) -> pd.DataFrame:
    """
    Load a team's saved schedule CSV. Return an empty DataFrame with expected
    columns if none exists or if the file is unreadable.
    """
    path = data_path / "schedules" / f"{_sanitize_text(team_id).replace(' ', '_')}_schedule.csv"
    if not path.exists():
        return pd.DataFrame(columns=["team_id"] + EXPECTED_COLUMNS)
    try:
        df = pd.read_csv(path, dtype=str)
    except Exception:
        return pd.DataFrame(columns=["team_id"] + EXPECTED_COLUMNS)
    df = df.fillna("")
    # Ensure expected columns
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    # Ensure team_id column exists and is first
    if "team_id" not in df.columns:
        df.insert(0, "team_id", _sanitize_text(team_id))
    else:
        df["team_id"] = df["team_id"].replace("", _sanitize_text(team_id))
        # Move to front if needed
        cols = ["team_id"] + [c for c in df.columns if c != "team_id"]
        df = df[cols]
    # Coerce event_date to strings in YYYY-MM-DD where possible
    if "event_date" in df.columns:
        df["event_date"] = df["event_date"].apply(_normalize_date)
    return df[["team_id"] + EXPECTED_COLUMNS]


def save_team_schedule(data_path: Path, team_id: str, df: pd.DataFrame) -> None:
    """
    Persist a team's schedule to CSV with sanitized, expected columns.
    Skips invalid rows instead of raising.
    """
    work = df.copy() if df is not None else pd.DataFrame(columns=EXPECTED_COLUMNS)
    for col in EXPECTED_COLUMNS:
        if col not in work.columns:
            work[col] = ""
    work = work.fillna("")

    cleaned_rows: List[Dict[str, str]] = []
    for _, row in work.iterrows():
        # Drop fully empty rows
        if all((str(row.get(col, "")).strip() == "") for col in EXPECTED_COLUMNS):
            continue

        date_raw = str(row.get("event_date", "")).strip()
        time_raw = str(row.get("start_time", "")).strip()
        if not date_raw or not time_raw:
            continue

        date_norm = _normalize_date(date_raw)
        time_norm = _normalize_time_12h(time_raw)
        # If still empty after normalization, skip
        if not date_norm or not time_norm:
            continue

        cleaned_rows.append(
            {
                "event_date": date_norm,
                "start_time": time_norm,
                "end_time": _sanitize_text(str(row.get("end_time", ""))),
                "event_type": _sanitize_text(str(row.get("event_type", ""))),
                "opponent": _sanitize_text(str(row.get("opponent", ""))),
                "location": _sanitize_text(str(row.get("location", ""))),
                "notes": _sanitize_text(str(row.get("notes", ""))),
            }
        )

    if not cleaned_rows:
        raise ValueError("No valid schedule rows to save")

    cleaned_df = pd.DataFrame(cleaned_rows)
    cleaned_df = _ensure_columns(cleaned_df)
    cleaned_df = cleaned_df.sort_values(["event_date", "start_time"])
    cleaned_df.insert(0, "team_id", _sanitize_text(team_id))

    path = data_path / "schedules" / f"{_sanitize_text(team_id).replace(' ', '_')}_schedule.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(path, index=False)
