"""Unit tests for LLM track helpers (no API calls)."""

from pathlib import Path

import pytest

from llmTest import _extract_python_from_response, _iter_source_files, _read_truncated


def test_extract_python_fenced():
    md = '''Here you go:\n```python\ndef test_x():\n    assert True\n```\n'''
    assert "def test_x()" in _extract_python_from_response(md)


def test_extract_python_plain():
    assert _extract_python_from_response("x = 1\n").strip() == "x = 1"


def test_extract_python_bare_fence_strips_outer_lines():
    text = "```\nx = 2\n```"
    assert _extract_python_from_response(text) == "x = 2"


def test_iter_source_files_missing_returns_empty(tmp_path: Path):
    missing = tmp_path / "nope"
    assert _iter_source_files(str(missing)) == []


def test_iter_source_files_skips_pycache_and_tests(tmp_path: Path):
    pkg = tmp_path / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "a.py").write_text("x = 1\n")
    (pkg / "test_skip.py").write_text("pass\n")
    nested = pkg / "sub"
    nested.mkdir()
    (nested / "b.py").write_text("y = 2\n")
    bad = pkg / "__pycache__"
    bad.mkdir()
    (bad / "x.pyc").write_bytes(b"a")
    found = _iter_source_files(str(pkg))
    names = sorted(str(p.relative_to(pkg)) for p in found)
    assert names == ["a.py", "sub\\b.py"]


def test_iter_source_files_ignores_nested_test_modules(tmp_path: Path):
    pkg = tmp_path / "pkg"
    pkg.mkdir(parents=True)
    sub = pkg / "subpkg"
    sub.mkdir()
    (sub / "test_inner.py").write_text("def test_fake():\n    assert True\n", encoding="utf-8")
    (sub / "real_module.py").write_text("VALUE = 1\n", encoding="utf-8")

    found = _iter_source_files(str(pkg))
    names = sorted(p.name for p in found)
    assert "test_inner.py" not in names
    assert "real_module.py" in names


def test_read_truncated_truncates(tmp_path: Path):
    p = tmp_path / "big.py"
    p.write_text("a" * 20_000)
    out = _read_truncated(p, max_chars=100)
    assert len(out) < 600
    assert "truncated" in out


def test_read_truncated_short_file_unchanged(tmp_path: Path):
    p = tmp_path / "small.py"
    p.write_text("print(1)", encoding="utf-8")
    assert _read_truncated(p, max_chars=10_000) == "print(1)"
