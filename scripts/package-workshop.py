#!/usr/bin/env python3
"""Create a reproducible, allowlisted workshop release using only the standard library."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import zipfile

VERSION = "2026.09-rc1"
TOP_FILES = {"README.md", "RELEASE.md", "VALIDATION.md",
             "pyproject.toml", "uv.lock", ".env.example", ".gitignore"}
EXTRA_FILES = {"build_lab/HARNESS_WORKSHEET.md"}
DIRECTORIES = {
    "course": {".py"}, "build_lab": {".py"}, "exercises": {".py"},
    "tests": {".py"}, "notebooks": {".ipynb"}, "skills": {".md"},
}
MANIFEST = "workshop/MANIFEST.json"
SECRET_PATTERNS = [
    re.compile(rb"sk-(?:or-v1-)?[A-Za-z0-9_-]{24,}"),
    re.compile(rb"(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"(?im)^[ \t]*(?:OPENROUTER_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY)[ \t]*=[ \t]*[^\s#]+"),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def allowed_member(name: str) -> bool:
    if name in {"workshop/" + path for path in EXTRA_FILES}:
        return True
    parts = PurePosixPath(name).parts
    if len(parts) == 2:
        return parts[0] == "workshop" and parts[1] in TOP_FILES
    return (len(parts) >= 3 and parts[0] == "workshop" and parts[1] in DIRECTORIES
            and all(not p.startswith(".") and p != "__pycache__" for p in parts[2:])
            and PurePosixPath(name).suffix in DIRECTORIES[parts[1]])


def validate_content(name: str, data: bytes) -> None:
    if any(pattern.search(data) for pattern in SECRET_PATTERNS):
        raise ValueError(f"Credential-like content rejected in {name}; content is not printed")
    if name.endswith(".ipynb"):
        notebook = json.loads(data)
        if any(cell.get("outputs") or cell.get("execution_count") is not None
               for cell in notebook["cells"]):
            raise ValueError(f"Notebook execution output/count must be cleared: {name}")
        if any(cell.get("attachments") for cell in notebook["cells"]):
            raise ValueError(f"Embedded notebook attachments are not release inputs: {name}")


def collect(source: Path) -> dict[str, bytes]:
    source = source.resolve(strict=True)
    candidates = [source / name for name in sorted(TOP_FILES | EXTRA_FILES)]
    for folder, suffixes in DIRECTORIES.items():
        base = source / folder
        if base.is_symlink():
            raise ValueError(f"Symlink input is not allowed: {folder}")
        if not base.is_dir():
            raise ValueError(f"Required directory missing: {folder}")
        # Do not traverse hidden directories, runtime caches or symlink directories.
        for current, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "__pycache__")
            if any((Path(current) / d).is_symlink() for d in dirs):
                raise ValueError(f"Symlink directory is not allowed under {folder}")
            candidates.extend(Path(current) / f for f in sorted(files)
                              if not f.startswith(".") and Path(f).suffix in suffixes)
    payload = {}
    for path in sorted(candidates):
        if not path.exists():
            raise ValueError(f"Required release input missing: {path.relative_to(source).as_posix()}")
        if path.is_symlink() or not path.resolve(strict=True).is_relative_to(source):
            raise ValueError("Input must be a regular file inside workshop")
        name = "workshop/" + path.relative_to(source).as_posix()
        data = path.read_bytes().replace(b"\r\n", b"\n")
        validate_content(name, data)
        payload[name] = data
    return payload


def archive_bytes(payload: dict[str, bytes]) -> bytes:
    manifest = {"version": VERSION, "files": {
        name: {"sha256": digest(data), "bytes": len(data)}
        for name, data in sorted(payload.items())
    }}
    files = {**payload, MANIFEST: (json.dumps(manifest, ensure_ascii=False, indent=2,
                                           sort_keys=True) + "\n").encode("utf-8")}
    result = io.BytesIO()
    # Stored entries avoid compressor/version-dependent output; all metadata is fixed.
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return result.getvalue()


def verify_archive(data: bytes) -> int:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate archive paths")
        for name in names:
            path = PurePosixPath(name)
            if (path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name
                    or not path.parts or path.parts[0] != "workshop" or path.as_posix() != name):
                raise ValueError("Unsafe archive path")
            if name != MANIFEST and not allowed_member(name):
                raise ValueError("Archive member is outside release allowlist")
            if (archive.getinfo(name).external_attr >> 16) != 0o100644:
                raise ValueError("Only regular files are allowed")
        manifest = json.loads(archive.read(MANIFEST))
        if manifest["version"] != VERSION or set(names) != set(manifest["files"]) | {MANIFEST}:
            raise ValueError("Manifest version/file list mismatch")
        with tempfile.TemporaryDirectory(prefix="workshop-release-check-") as folder:
            root = Path(folder).resolve()
            archive.extractall(root)  # Every name and file type was checked above.
            for name, expected in manifest["files"].items():
                path = root / name
                if not path.resolve().is_relative_to(root):
                    raise ValueError("Extracted path escaped verification directory")
                content = path.read_bytes()
                if expected != {"sha256": digest(content), "bytes": len(content)}:
                    raise ValueError(f"Manifest hash mismatch: {name}")
                validate_content(name, content)
    return len(manifest["files"])


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as file:
        temp = Path(file.name)
        file.write(data)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify archive contents against current sources")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = root / "book/public/downloads" / f"agent-workshop-{VERSION}.zip"
    expected = archive_bytes(collect(root / "workshop"))
    data = target.read_bytes() if args.check else expected
    count = verify_archive(data)
    if args.check:
        if data != expected:
            raise ValueError("Release archive differs from current sources; regenerate it")
    else:
        atomic_write(target, data)
        # Remove only the obsolete checksum sidecar for this release.
        target.with_suffix(".sha256").unlink(missing_ok=True)
    print(f"Verified {VERSION}: {count} files + manifest; SHA256 {digest(data)}")


if __name__ == "__main__":
    main()
