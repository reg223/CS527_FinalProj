"""Mocked coverage path for LLMTrackEvaluator.run_coverage_analysis (no API calls)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from llmTest import LLMTrackEvaluator


def test_llm_track_coverage_writes_same_keys(tmp_path, monkeypatch):
    report_json = {
        "totals": {
            "percent_covered": 77.7,
            "covered_branches": 11,
        }
    }

    ev = LLMTrackEvaluator(
        repo_path=str(tmp_path / "llm_tests"),
        source_dir=str(tmp_path / "pkg"),
        report_path=str(tmp_path / "out"),
    )

    def fake_run(cmd, check=False, env=None, **_kwargs):  # noqa: ARG001
        assert env is None or isinstance(env, dict)
        if cmd[:2] == ["coverage", "json"]:
            Path(ev.report_path).write_text(json.dumps(report_json), encoding="utf-8")
        return MagicMock(returncode=0)

    monkeypatch.chdir(tmp_path)

    with patch("llmTest.subprocess.run", side_effect=fake_run):
        ev.run_coverage_analysis()

    assert ev.results["overall_precision"] == 77.7
    assert ev.results["branch_coverage"] == 11


def test_generate_without_api_key_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    pkg = tmp_path / "widgets"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "core.py").write_text("def f():\n    return 42\n", encoding="utf-8")

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    ev = LLMTrackEvaluator(
        repo_path=str(tmp_path / "llm_tests"),
        source_dir=str(pkg),
        api_key=None,
        max_revision_attempts=1,
    )
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        ev.generate_and_validate_tests()
