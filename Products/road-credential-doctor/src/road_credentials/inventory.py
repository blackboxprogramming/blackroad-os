from __future__ import annotations

import re
from collections import defaultdict
from fnmatch import fnmatch
from typing import Any

from .models import Credential, SecretReference, Settings
from .scanner import iter_text_files


NAME_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
SECRET_MARKERS = (
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "API_KEY",
    "PRIVATE_KEY",
    "ACCESS_KEY",
    "SIGNING_KEY",
    "ENCRYPTION_KEY",
)
EXCLUDED_MARKERS = ("PUBLIC_KEY", "KEY_ID", "KEY_NAME", "KEY_PATH", "KEY_FILE")
SPECIAL_SECRET_NAMES = {"DATABASE_URL", "REDIS_URL", "MONGO_URL", "MONGODB_URI"}


def _secretish(name: str) -> bool:
    if any(marker in name for marker in EXCLUDED_MARKERS):
        return False
    return name in SPECIAL_SECRET_NAMES or any(marker in name for marker in SECRET_MARKERS)


def _syntax(line: str, name: str) -> str:
    escaped = re.escape(name)
    if re.search(rf"secrets\s*\.\s*{escaped}\b", line):
        return "github_actions_secret"
    if re.search(rf"process\.env\.{escaped}\b", line):
        return "javascript_env"
    if re.search(rf"(?:os\.environ\s*\[|getenv\s*\()[\"']{escaped}[\"']", line):
        return "python_env"
    if re.search(rf"os\.Getenv\s*\([\"']{escaped}[\"']", line):
        return "go_env"
    if re.search(rf"env::var\s*\([\"']{escaped}[\"']", line):
        return "rust_env"
    if re.search(rf"ENV\s*\[[\"']{escaped}[\"']", line):
        return "ruby_env"
    if re.search(rf"\$\{{?{escaped}\}}?", line):
        return "shell_env"
    if re.search(rf"^\s*(?:export\s+)?{escaped}\s*=", line):
        return "env_definition"
    if re.search(rf"\b(?:key|secretKeyRef)\s*:\s*[\"']?{escaped}\b", line):
        return "orchestrator_secret_ref"
    return "named_reference"


def discover_references(settings: Settings) -> list[SecretReference]:
    known_names = {name for credential in settings.credentials for name in credential.names}
    config_relative: str | None = None
    try:
        config_relative = settings.config_path.relative_to(settings.root).as_posix()
    except ValueError:
        pass
    unique: dict[tuple[str, int, str, str], SecretReference] = {}
    for path, text in iter_text_files(settings):
        if path == config_relative or any(fnmatch(path, pattern) for pattern in settings.reference_ignore_paths):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            candidates = {name for name in NAME_PATTERN.findall(line) if name in known_names or _secretish(name)}
            for name in candidates:
                syntax = _syntax(line, name)
                reference = SecretReference(path, line_number, name, syntax)
                unique[(path, line_number, name, syntax)] = reference
    return sorted(unique.values(), key=lambda item: (item.path, item.line, item.name, item.syntax))


def _consumer_covers(credential: Credential, path: str) -> list[str]:
    return [
        consumer.id
        for consumer in credential.consumers
        if consumer.paths and any(fnmatch(path, pattern) for pattern in consumer.paths)
    ]


def coverage_report(settings: Settings) -> dict[str, Any]:
    references = discover_references(settings)
    by_name: dict[str, list[Credential]] = defaultdict(list)
    for credential in settings.credentials:
        for name in credential.names:
            by_name[name].append(credential)
    covered: list[dict[str, Any]] = []
    uncovered: list[dict[str, Any]] = []
    unregistered: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for reference in references:
        matches = by_name.get(reference.name, [])
        public = reference.public()
        if not matches:
            unregistered.append(public)
            continue
        if len(matches) > 1:
            ambiguous.append({**public, "credentials": [item.id for item in matches]})
            continue
        credential = matches[0]
        consumers = _consumer_covers(credential, reference.path)
        entry = {**public, "credential_id": credential.id, "consumers": consumers}
        if consumers:
            covered.append(entry)
        else:
            uncovered.append(entry)
    return {
        "references": len(references),
        "covered": covered,
        "uncovered": uncovered,
        "unregistered": unregistered,
        "ambiguous": ambiguous,
    }


def blockers_for_credentials(report: dict[str, Any], credential_ids: set[str], *, include_unregistered: bool) -> list[dict[str, Any]]:
    blockers = [item for item in report["uncovered"] if item.get("credential_id") in credential_ids]
    blockers.extend(
        item
        for item in report["ambiguous"]
        if credential_ids.intersection(item.get("credentials", []))
    )
    if include_unregistered:
        blockers.extend(report["unregistered"])
    return blockers
