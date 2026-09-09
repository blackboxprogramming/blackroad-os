from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    fingerprint: str
    source: str = "working_tree"

    def public(self, *, retired: bool = False) -> dict[str, Any]:
        return {
            "path": self.path,
            "line": self.line,
            "kind": self.kind,
            "fingerprint": self.fingerprint,
            "source": self.source,
            "status": "retired" if retired else "active",
        }


@dataclass(frozen=True)
class CommandSpec:
    argv: tuple[str, ...]
    timeout_seconds: int = 60


@dataclass(frozen=True)
class Consumer:
    id: str
    paths: tuple[str, ...]
    update_action: str
    verify_action: str
    rollback_action: str


@dataclass(frozen=True)
class Credential:
    id: str
    connector: str
    risk: str
    provider_id: str | None
    kinds: tuple[str, ...]
    names: tuple[str, ...]
    paths: tuple[str, ...]
    fingerprints: tuple[str, ...]
    auto_heal: bool
    authorize_action: str | None
    create_action: str
    validate_action: str
    activate_action: str
    restore_action: str
    revoke_old_action: str
    revoke_new_action: str
    consumers: tuple[Consumer, ...]

    def matches(self, finding: Finding) -> bool:
        from fnmatch import fnmatch

        if self.kinds and finding.kind not in self.kinds:
            return False
        if self.fingerprints and finding.fingerprint not in self.fingerprints:
            return False
        candidate_path = finding.path
        if finding.source == "git_history" and candidate_path.startswith("git:"):
            candidate_path = candidate_path.split(":", 2)[-1]
        return not self.paths or any(fnmatch(candidate_path, pattern) for pattern in self.paths)


@dataclass(frozen=True)
class Settings:
    config_path: Path
    root: Path
    state_file: Path
    receipt_dir: Path
    ignore_file: Path
    max_file_bytes: int
    history_max_bytes: int
    reference_ignore_paths: tuple[str, ...]
    connector_runtime_id: str
    connector_dispatch: CommandSpec
    credentials: tuple[Credential, ...]


@dataclass(frozen=True)
class SecretReference:
    path: str
    line: int
    name: str
    syntax: str

    def public(self) -> dict[str, Any]:
        return {"path": self.path, "line": self.line, "name": self.name, "syntax": self.syntax}
