"""Team schedule utilities: parsing, storage, and conversions."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional

import pandas as pd

SCHEDULE_COLUMNS = ["date", "time", "type", "opponent", "location", "notes", "source"]


@dataclass
class ScheduleEvent:
    date: date
    time: str
    type: str
    opponent: str = ""
    location: str = ""
    notes: str = ""
    source: str = "parsed"

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else str(self.date),
            "time": self.time,
            "type": self.type,
            "opponent": self.opponent,
            "location": self.location,
            "notes": self.notes,
            "source": self.source,
        }


def get_schedule_path(data_path: Path, team_id: str) -> Path:
    return Path(data_path) / f"practice_game_schedule_{team_id}.csv"


def load_schedule(data_path: Path, team_id: str) -> pd.DataFrame:
    path = get_schedule_path(data_path, team_id)
    if not path.exists():
        return pd.DataFrame(columns=SCHEDULE_COLUMNS)
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=SCHEDULE_COLUMNS)
    for col in SCHEDULE_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[SCHEDULE_COLUMNS]


def save_schedule(data_path: Path, team_id: str, df: pd.DataFrame) -> None:
    path = get_schedule_path(data_path, team_id)
    clean = df.copy()
    for col in ["date", "time", "type", "opponent", "location", "notes", "source"]:
        if col in clean.columns:
            clean[col] = clean[col].astype(str).str.strip()
    if "date" in clean.columns:
        clean = clean[clean["date"] != ""]
    if "type" in clean.columns:
        clean = clean[clean["type"] != ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(path, index=False)


def _extract_date(line: str) -> Optional[date]:
    patterns = [
        (r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", ["%m/%d/%Y", "%m/%d/%y"]),
        (r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}\b",
         ["%B %d, %Y", "%b %d, %Y"]),
    ]
    for regex, fmts in patterns:
        match = re.search(regex, line, flags=re.IGNORECASE)
        if not match:
            continue
        text = match.group(0)
        for fmt in fmts:
            try:
                return datetime.strptime(text, fmt).date()
            except Exception:
                continue
    return None


def _extract_time(line: str) -> str:
    match = re.search(r"\b\d{1,2}:\d{2}\s*(am|pm)?\b", line, flags=re.IGNORECASE)
    if match:
        raw = match.group(0).replace(" ", "")
        try:
            parsed = datetime.strptime(raw.upper(), "%I:%M%p")
            return parsed.strftime("%I:%M %p").lstrip("0")
        except Exception:
            return raw
    match = re.search(r"\b\d{1,2}\s*(am|pm)\b", line, flags=re.IGNORECASE)
    if match:
        raw = match.group(0).replace(" ", "")
        try:
            parsed = datetime.strptime(raw.upper(), "%I%p")
            return parsed.strftime("%I:%M %p").lstrip("0")
        except Exception:
            return raw
    return ""


def _infer_type(line: str) -> str:
    lower = line.lower()
    if any(word in lower for word in ["practice", "training"]):
        return "practice"
    if any(word in lower for word in ["game", "match", "scrimmage"]):
        return "game"
    return "practice"


def _extract_opponent(line: str) -> str:
    match = re.search(r"(vs\.?|@)\s+([A-Za-z0-9].+)", line, flags=re.IGNORECASE)
    if match:
        return match.group(2).strip()
    return ""


def _extract_location(line: str) -> str:
    keywords = ["field", "stadium", "complex", "park", "facility", "at"]
    lower = line.lower()
    positions = [lower.find(k) for k in keywords if k in lower]
    if not positions:
        return ""
    start = min(pos for pos in positions if pos >= 0)
    return line[start:].strip()


def parse_schedule_pdf(file_obj) -> List[ScheduleEvent]:
    try:
        import pdfplumber
    except Exception:
        raise RuntimeError("pdfplumber is required to parse PDF schedules. Please install it.")

    events: List[ScheduleEvent] = []
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                evt_date = _extract_date(line)
                if not evt_date:
                    continue
                evt_time = _extract_time(line)
                evt_type = _infer_type(line)
                evt_opponent = _extract_opponent(line)
                evt_location = _extract_location(line)
                events.append(
                    ScheduleEvent(
                        date=evt_date,
                        time=evt_time,
                        type=evt_type,
                        opponent=evt_opponent,
                        location=evt_location,
                        notes=raw_line,
                        source="parsed",
                    )
                )
    return events


def events_to_dataframe(events: List[ScheduleEvent]) -> pd.DataFrame:
    if not events:
        return pd.DataFrame(columns=SCHEDULE_COLUMNS)
    records = [evt.to_dict() for evt in events]
    df = pd.DataFrame(records)
    return df[SCHEDULE_COLUMNS]
