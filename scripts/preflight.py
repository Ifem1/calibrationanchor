from __future__ import annotations

from pathlib import Path
import ast
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "SUBMISSION.md",
    "DEPLOYMENT.md",
    "AGENTS.md",
    "contracts/calibrationanchor.py",
    "contracts/calibration_gate.py",
    "tests/direct/test_calibrationanchor.py",
    "tests/direct/test_hardening.py",
    "docs/ARCHITECTURE.md",
    "docs/CONSENSUS.md",
    "docs/THREAT_MODEL.md",
    "docs/REVIEWER_GUIDE.md",
    "gltest.config.yaml",
]

FORBIDDEN_TEXT = [
    "619" + "97",
    "studio" + "-dev.genlayer.com",
    "explorer-studio" + "-dev.genlayer.com",
]

REQUIRED_CONTRACT_SNIPPETS = [
    "class CalibrationAnchor(gl.Contract)",
    "gl.vm.run_nondet_unsafe",
    "RUNTIME_INPUT_DRIFT",
    "CAL_STABLE",
    "def is_latest_stable",
    "def finalize_run",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


for rel in REQUIRED:
    path = ROOT / rel
    if not path.exists():
        fail(f"missing required file: {rel}")

if (ROOT / "frontend").exists():
    fail("frontend directory must not exist for this standalone contract submission")

all_text = []
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if ".git" in path.parts or "__pycache__" in path.parts:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    all_text.append((path, text))

for path, text in all_text:
    for forbidden in FORBIDDEN_TEXT:
        if forbidden in text:
            fail(f"forbidden network target {forbidden!r} found in {path.relative_to(ROOT)}")

combined = "\n".join(text for _, text in all_text)
for required in ("61999", "https://studio.genlayer.com/api", "studionet"):
    if required not in combined:
        fail(f"required stable Studionet marker missing: {required}")

contract_path = ROOT / "contracts/calibrationanchor.py"
contract_text = contract_path.read_text(encoding="utf-8")
for snippet in REQUIRED_CONTRACT_SNIPPETS:
    if snippet not in contract_text:
        fail(f"main contract missing required mechanism: {snippet}")

for rel in ("contracts/calibrationanchor.py", "contracts/calibration_gate.py"):
    path = ROOT / rel
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        fail(f"syntax error in {rel}: {exc}")

fixture = ROOT / "fixtures/example_cases.json"
try:
    parsed = json.loads(fixture.read_text(encoding="utf-8"))
except Exception as exc:
    fail(f"fixture JSON invalid: {exc}")
if not isinstance(parsed, list) or len(parsed) < 3:
    fail("example fixture must contain at least three cases")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
for phrase in (
    "no frontend",
    "INPUT_DRIFT",
    "INSUFFICIENT_COVERAGE",
    "is_latest_stable",
):
    if phrase.lower() not in readme.lower():
        fail(f"README missing reviewer-facing concept: {phrase}")

print("CalibrationAnchor preflight: PASS")
print(f"Checked {len(REQUIRED)} required files and {len(all_text)} text files.")
print("Network lock: Studionet 61999 only.")
