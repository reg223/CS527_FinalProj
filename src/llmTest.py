"""LLM track: generate pytest suites via an OpenAI-compatible API, validate with pytest, then reuse coverage/complexity analysis."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from humanTest import HumanTrackEvaluator

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional until requirements installed
    OpenAI = None  # type: ignore[misc, assignment]


DEFAULT_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
DEFAULT_MAX_ATTEMPTS = int(os.environ.get("LLM_TEST_MAX_ATTEMPTS", "3"))
GENERATED_FILENAME = "test_llm_generated_suite.py"


def _iter_source_files(source_root: str) -> List[Path]:
    root = Path(source_root)
    if not root.is_dir():
        return []
    out: List[Path] = []
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        if p.name.startswith("test_"):
            continue
        out.append(p)
    return sorted(out)


def _read_truncated(path: Path, max_chars: int = 14_000) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        return text[:max_chars] + "\n# ... [truncated for prompt size] ...\n"
    return text


def _extract_python_from_response(text: str) -> str:
    """Pull the first fenced ```python ``` block; else strip a bare ``` wrapper; else return stripped text."""
    m = re.search(r"```(?:python)?\s*\n([\s\S]*?)```", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2:
            return "\n".join(lines[1:-1]).strip()
    return text


class LLMTrackEvaluator(HumanTrackEvaluator):
    """
    Mirrors the human track evaluator: same ``run_coverage_analysis`` /
    ``run_complexity_analysis`` from the base class after tests exist under ``repo_path``.

    Typical flow::

        eval = LLMTrackEvaluator(
            repo_path="testsuites/loguru/llm_tests",
            source_dir="testsuites/loguru/loguru",
            report_path="reports/loguru_llm",
        )
        eval.generate_and_validate_tests()
        eval.run_coverage_analysis()
        eval.run_complexity_analysis()
    """

    def __init__(
        self,
        repo_path: str,
        source_dir: str,
        report_path: Optional[str] = None,
        max_revision_attempts: Optional[int] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        generated_filename: str = GENERATED_FILENAME,
    ):
        super().__init__(repo_path=repo_path, source_dir=source_dir, report_path=report_path)
        self.max_revision_attempts = (
            DEFAULT_MAX_ATTEMPTS if max_revision_attempts is None else max_revision_attempts
        )
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or DEFAULT_MODEL
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        self.generated_filename = generated_filename
        self._last_pytest_stderr = ""

    def _client(self):
        if OpenAI is None:
            raise RuntimeError("Install the 'openai' package (pip install -r requirements.txt).")
        if not self.api_key:
            raise RuntimeError(
                "Set OPENAI_API_KEY or pass api_key=... to LLMTrackEvaluator for the LLM track."
            )
        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return OpenAI(**kwargs)

    def _package_hint(self) -> str:
        return Path(self.source_dir).name

    def _build_zero_shot_prompt(self, source_snippets: List[Tuple[str, str]]) -> str:
        pkg = self._package_hint()
        files_desc = "\n\n".join(
            f"### File: {rel}\n```python\n{body}\n```" for rel, body in source_snippets
        )
        return f"""You write pytest unit tests for an existing Python package.

Package import name (top-level): `{pkg}`

Source files (relative paths under the package root):

{files_desc}

Requirements:
- Output a single Python module only: valid pytest tests, no prose outside code.
- Use `import {pkg}` or `from {pkg} import ...` as appropriate.
- Prefer fast, deterministic tests; avoid network and real filesystem side effects where possible.
- Name test functions `test_*`.
- If the API needs temp paths, use `tmp_path` from pytest or `tempfile`.
- Start the code block with ```python and end with ```.

Generate one complete test file."""

    def _build_revision_prompt(self, previous_code: str, pytest_output: str) -> str:
        return f"""The following pytest test file failed. Fix it so `pytest` passes on this file only.

Previous code:
```python
{previous_code}
```

Pytest/collection errors (stderr/stdout):
```
{pytest_output[:12000]}
```

Return the full corrected Python file in one ```python fenced block. No explanation outside the code block."""

    def _write_generated_file(self, code: str) -> Path:
        out_dir = Path(self.repo_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / self.generated_filename
        path.write_text(code.strip() + "\n", encoding="utf-8")
        return path

    def _run_pytest_smoke(self) -> Tuple[int, str]:
        """Run pytest only on the LLM test directory (fast validation)."""
        cmd = [
            os.environ.get("PYTHON", "python"),
            "-m",
            "pytest",
            str(Path(self.repo_path)),
            "-q",
            "--tb=short",
            "--no-header",
        ]
        env = os.environ.copy()
        # Allow imports of the vendored package next to testsuites layout
        src_parent = str(Path(self.source_dir).resolve().parent)
        env["PYTHONPATH"] = src_parent + os.pathsep + env.get("PYTHONPATH", "")

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
        )
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        self._last_pytest_stderr = out.strip()
        return proc.returncode, out

    def _chat(self, user_prompt: str) -> str:
        client = self._client()
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python test engineer. Obey output format instructions exactly.",
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        choice = resp.choices[0].message
        return (choice.content or "").strip()

    def generate_and_validate_tests(self) -> Path:
        """
        Generate tests with the LLM, then revise up to ``max_revision_attempts`` times using pytest output.
        Persistently failing generations leave the last attempt on disk; callers may discard or inspect.
        """
        sources = _iter_source_files(self.source_dir)
        if not sources:
            raise FileNotFoundError(
                f"No Python sources under {self.source_dir!r}; cannot run LLM track."
            )

        snippets: List[Tuple[str, str]] = []
        for p in sources:
            rel = str(p.relative_to(Path(self.source_dir)))
            snippets.append((rel, _read_truncated(p)))

        prompt = self._build_zero_shot_prompt(snippets)
        raw = self._chat(prompt)
        code = _extract_python_from_response(raw)
        path = self._write_generated_file(code)

        for attempt in range(self.max_revision_attempts):
            rc, output = self._run_pytest_smoke()
            if rc == 0:
                print(f"--- LLM tests validated with pytest ({path}) ---")
                return path
            if attempt == self.max_revision_attempts - 1:
                print(
                    f"--- LLM tests still failing after {self.max_revision_attempts} attempt(s); "
                    f"keeping last version at {path} ---"
                )
                return path
            fix_prompt = self._build_revision_prompt(path.read_text(encoding="utf-8"), output)
            fixed_raw = self._chat(fix_prompt)
            code = _extract_python_from_response(fixed_raw)
            path = self._write_generated_file(code)

        return path

    def run_coverage_analysis(self):
        """Run pytest under Coverage.py with branch coverage; same as human track but honors PYTHONPATH for imports."""
        print(f"--- Running Coverage.py (LLM track) on {self.repo_path} ---")
        env = os.environ.copy()
        src_parent = str(Path(self.source_dir).resolve().parent)
        env["PYTHONPATH"] = src_parent + os.pathsep + env.get("PYTHONPATH", "")

        cmd = [
            "coverage",
            "run",
            "--branch",
            f"--source={self.source_dir}",
            "-m",
            "pytest",
            str(self.repo_path),
        ]
        subprocess.run(cmd, check=True, env=env)

        subprocess.run(["coverage", "json", "-o", self.report_path], check=True, env=env)

        with open(self.report_path, encoding="utf-8") as f:
            data = json.load(f)
            self.results["overall_precision"] = data["totals"]["percent_covered"]
            self.results["branch_coverage"] = data["totals"]["covered_branches"]
