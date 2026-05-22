import sys
from pathlib import Path
import tempfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import data_loader

def test_load_mentor_feed_missing():
    # If the mentor_feed.json does not exist in the path, it should return {"posts": []}
    with tempfile.TemporaryDirectory() as tmpdir:
        res = data_loader.load_mentor_feed(tmpdir)
        assert res == {"posts": []}

def test_save_and_load_mentor_feed():
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_data = {
            "posts": [
                {
                    "post_id": "POST_002",
                    "presenter_id": "UNLV-01",
                    "title": "Older Post",
                    "date_posted": "2026-05-10"
                },
                {
                    "post_id": "POST_001",
                    "presenter_id": "KC-01",
                    "title": "Newer Post",
                    "date_posted": "2026-05-20"
                }
            ]
        }
        
        # Save feed
        data_loader.save_mentor_feed(feed_data, tmpdir)
        
        # Load feed - should be sorted newest first (POST_001 then POST_002)
        loaded = data_loader.load_mentor_feed(tmpdir)
        assert len(loaded["posts"]) == 2
        assert loaded["posts"][0]["post_id"] == "POST_001"
        assert loaded["posts"][1]["post_id"] == "POST_002"

def test_load_mentor_feed_malformed():
    with tempfile.TemporaryDirectory() as tmpdir:
        feed_path = Path(tmpdir) / "mentor_feed.json"
        # Write invalid JSON content
        with open(feed_path, "w", encoding="utf-8") as f:
            f.write("invalid json content")
            
        res = data_loader.load_mentor_feed(tmpdir)
        assert res == {"posts": []}
