from __future__ import annotations

from pathlib import Path

from lab.models import PROTECTED_PATH

_FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "fake_repo"


class FakeRepo:
    """In-memory tree seeded from fixtures/fake_repo. No network."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}
        if _FIXTURE_ROOT.is_dir():
            for path in _FIXTURE_ROOT.rglob("*"):
                if path.is_file():
                    rel = path.relative_to(_FIXTURE_ROOT).as_posix()
                    self.files[rel] = path.read_text(encoding="utf-8")
        self.files.setdefault(PROTECTED_PATH, '{"policy": "frozen-v0.2"}\n')

    def read(self, path: str) -> str:
        return self.files.get(path, "")
