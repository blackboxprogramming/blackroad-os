from __future__ import annotations

import hashlib
import math
import os
import re
import subprocess
from collections import Counter
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, Iterator

from .models import Finding, Settings


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,255}|github_pat_[A-Za-z0-9_]{20,255})\b")),
    ("openai_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,255}\b")),
    ("stripe_secret", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,255}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,255}\b")),
    ("sendgrid_key", re.compile(r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("digitalocean_token", re.compile(r"\bdop_v1_[a-fA-F0-9]{64}\b")),
    ("npm_token", re.compile(r"\bnpm_[A-Za-z0-9]{36,}\b")),
    ("pypi_token", re.compile(r"\bpypi-[A-Za-z0-9_-]{50,}\b")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("gitlab_token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("tailscale_key", re.compile(r"\btskey-[A-Za-z0-9_-]{20,}\b")),
    ("terraform_cloud_token", re.compile(r"\batlasv1\.[A-Za-z0-9_-]{40,}\b")),
    ("stripe_webhook_secret", re.compile(r"\bwhsec_[A-Za-z0-9]{16,255}\b")),
    ("age_secret_key", re.compile(r"\bAGE-SECRET-KEY-[A-Z0-9]{20,}\b")),
)

PRIVATE_KEY_HEADER = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")
PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN (?P<label>(?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY)-----"
    r"[\s\S]{1,32768}?"
    r"-----END (?P=label)-----"
)

GENERIC_ASSIGNMENT = re.compile(
    r"(?i)(?:api[_-]?key|secret|token|password|private[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9_+/.=-]{20,512})"
)

DEFAULT_IGNORED_DIRS = {
    ".git",
    ".road-credentials",
    ".venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "__pycache__",
}
BINARY_SUFFIXES = {
    ".7z", ".avi", ".bin", ".bmp", ".class", ".dmg", ".doc", ".docx", ".eot", ".exe",
    ".gif", ".gz", ".ico", ".jar", ".jpeg", ".jpg", ".mov", ".mp3", ".mp4", ".o", ".pdf",
    ".png", ".pyc", ".so", ".tar", ".tgz", ".ttf", ".wav", ".webm", ".webp", ".woff", ".woff2",
    ".xls", ".xlsx", ".xz", ".zip",
}


class ScanIncomplete(RuntimeError):
    pass


def fingerprint(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8", "surrogatepass")).hexdigest()


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def _looks_like_code_reference(value: str) -> bool:
    lowered = value.lower()
    return bool(
        re.match(r"^(?:sys|os|process|config|settings|self|request|response|runtime|secret)\.", lowered)
        or any(fragment in lowered for fragment in (".read", ".getenv", ".environ", ".token_urlsafe"))
    )


def _line_findings(text: str, path: str, line_number: int, source: str) -> Iterable[Finding]:
    spans: list[tuple[int, int]] = []
    for kind, pattern in PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(0)
            spans.append(match.span())
            yield Finding(path, line_number, kind, fingerprint(value), source)
    for match in GENERIC_ASSIGNMENT.finditer(text):
        value = match.group(1)
        if (
            _entropy(value) < 3.2
            or _looks_like_code_reference(value)
            or any(start <= match.start(1) < end for start, end in spans)
        ):
            continue
        yield Finding(path, line_number, "generic_secret", fingerprint(value), source)
    if source == "git_history" and PRIVATE_KEY_HEADER.search(text):
        marker = f"{path}:{line_number}:private-key"
        yield Finding(path, line_number, "private_key", fingerprint(marker), source)


def _ignore_patterns(path: Path) -> tuple[str, ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return ()
    return tuple(line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#"))


def iter_text_files(settings: Settings) -> Iterator[tuple[str, str]]:
    root = settings.root
    ignores = _ignore_patterns(settings.ignore_file)
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        rel_dir = current_path.relative_to(root).as_posix()
        dirs[:] = [
            name
            for name in dirs
            if name not in DEFAULT_IGNORED_DIRS
            and not any(fnmatch(f"{rel_dir}/{name}".lstrip("./"), pattern) for pattern in ignores)
        ]
        for name in files:
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            if any(fnmatch(relative, pattern) for pattern in ignores):
                continue
            if path.suffix.lower() in BINARY_SUFFIXES or path.is_symlink():
                continue
            try:
                size = path.stat().st_size
                if size > settings.max_file_bytes:
                    with path.open("rb") as handle:
                        prefix = handle.read(4096)
                    if b"\x00" in prefix:
                        continue
                    raise ScanIncomplete(
                        f"text-like file exceeds max_file_bytes={settings.max_file_bytes}: {relative}"
                    )
                data = path.read_bytes()
            except ScanIncomplete:
                raise
            except (OSError, PermissionError) as exc:
                raise ScanIncomplete(f"file could not be scanned: {relative}") from exc
            if b"\x00" in data[:4096]:
                continue
            text = data.decode("utf-8", "replace")
            yield relative, text


def scan_working_tree(settings: Settings) -> list[Finding]:
    findings: list[Finding] = []
    for relative, text in iter_text_files(settings):
        for match in PRIVATE_KEY_BLOCK.finditer(text):
            value = match.group(0)
            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(Finding(relative, line_number, "private_key", fingerprint(value), "working_tree"))
        for number, line in enumerate(text.splitlines(), start=1):
            findings.extend(_line_findings(line, relative, number, "working_tree"))
    return _deduplicate(findings)


def scan_git_history(settings: Settings) -> list[Finding]:
    if not (settings.root / ".git").exists():
        return []
    command = ["git", "log", "--all", "--no-ext-diff", "--no-color", "-p", "--format=commit:%H"]
    process = subprocess.Popen(
        command,
        cwd=settings.root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    findings: list[Finding] = []
    consumed = 0
    truncated = False
    commit = "unknown"
    path = "unknown"
    assert process.stdout is not None
    try:
        for line in process.stdout:
            consumed += len(line.encode("utf-8", "replace"))
            if consumed > settings.history_max_bytes:
                truncated = True
                process.terminate()
                break
            if line.startswith("commit:"):
                commit = line.removeprefix("commit:").strip()[:12]
            elif line.startswith("+++ b/"):
                path = line.removeprefix("+++ b/").strip()
            elif line.startswith("+") and not line.startswith("+++"):
                location = f"git:{commit}:{path}"
                findings.extend(_line_findings(line[1:], location, 0, "git_history"))
    finally:
        process.stdout.close()
        if process.poll() is None:
            process.terminate()
        returncode = process.wait(timeout=5)
    if truncated:
        raise ScanIncomplete(
            f"Git history scan exceeded history_max_bytes={settings.history_max_bytes}; raise the configured limit"
        )
    if returncode != 0:
        raise ScanIncomplete(f"Git history scan failed with exit code {returncode}")
    return _deduplicate(findings)


def scan(settings: Settings, *, include_history: bool = False) -> list[Finding]:
    findings = scan_working_tree(settings)
    if include_history:
        findings.extend(scan_git_history(settings))
    return _deduplicate(findings)


def looks_like_secret(text: str) -> bool:
    return any(_line_findings(text, "<command>", 0, "configuration"))


def _deduplicate(findings: Iterable[Finding]) -> list[Finding]:
    unique: dict[tuple[str, int, str, str], Finding] = {}
    for finding in findings:
        key = (finding.path, finding.line, finding.kind, finding.fingerprint)
        unique[key] = finding
    return sorted(unique.values(), key=lambda x: (x.source, x.path, x.line, x.kind, x.fingerprint))
