import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import templates  # noqa: E402
import data_loader  # noqa: E402


def _tmp_dir():
    base = ROOT / "temp" / "template_tests"
    base.mkdir(parents=True, exist_ok=True)
    return base


def test_template_loader_round_trip(monkeypatch):
    tmp_path = _tmp_dir()
    # Point template storage to tmp_path
    monkeypatch.setattr(templates, "_template_path", lambda: tmp_path / "block_templates.json")
    monkeypatch.setattr(templates, "_backup_dir", lambda: tmp_path / "backups")

    demo = templates.BlockTemplate(
        name="Test Template",
        description="Demo",
        blocks={"warmup": ["W1"], "technical": ["T1"]},
        block_durations={"warmup": 10, "technical": 20},
    )
    templates.save_block_templates([demo])

    loaded = data_loader.load_session_templates(tmp_path)
    assert len(loaded) == 1
    tpl = loaded[0]
    assert tpl.name == "Test Template"
    assert tpl.blocks["warmup"] == ["W1"]
    assert tpl.block_durations.get("technical") == 20


def test_template_loader_handles_empty(monkeypatch):
    tmp_path = _tmp_dir()
    # Ensure clean slate
    (tmp_path / "block_templates.json").unlink(missing_ok=True)
    monkeypatch.setattr(templates, "_template_path", lambda: tmp_path / "block_templates.json")
    monkeypatch.setattr(templates, "_backup_dir", lambda: tmp_path / "backups")
    loaded = data_loader.load_session_templates(tmp_path)
    assert loaded == []
