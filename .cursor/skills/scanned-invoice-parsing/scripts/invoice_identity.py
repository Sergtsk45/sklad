#!/usr/bin/env python3
"""
@file: invoice_identity.py
@description: Отпечаток PDF-счёта (sha256/inode) и поиск копий с тем же содержимым
@dependencies: stdlib
@created: 2026-09-15
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

CHUNK = 1024 * 1024
SKIP_SUFFIXES = (":Zone.Identifier", ".Zone.Identifier")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sidecar(path: Path) -> bool:
    name = path.name
    return any(name.endswith(suffix) or suffix in name for suffix in SKIP_SUFFIXES)


def find_same_bytes(path: Path, scan_dir: Path | None = None) -> list[str]:
    """Пути в каталоге с тем же sha256, кроме самого файла и Windows ADS."""
    target = path.resolve()
    directory = (scan_dir or target.parent).resolve()
    digest = sha256_file(target)
    matches: list[str] = []
    if not directory.is_dir():
        return matches
    for candidate in sorted(directory.iterdir()):
        if not candidate.is_file() or _is_sidecar(candidate):
            continue
        resolved = candidate.resolve()
        if resolved == target:
            continue
        try:
            if sha256_file(resolved) == digest:
                matches.append(str(resolved))
        except OSError:
            continue
    return matches


def file_identity(path: Path, scan_dir: Path | None = None) -> dict:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(str(path))
    stat = resolved.stat()
    digest = sha256_file(resolved)
    return {
        "path": str(path),
        "realpath": str(resolved),
        "sha256": digest,
        "size": stat.st_size,
        "mtime": int(stat.st_mtime),
        "inode": stat.st_ino,
        "nlink": stat.st_nlink,
        "same_bytes": find_same_bytes(resolved, scan_dir=scan_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fingerprint an invoice file; find same-bytes copies in a directory",
    )
    parser.add_argument("pdf", type=Path, help="Path to invoice file")
    parser.add_argument(
        "--scan-dir",
        type=Path,
        default=None,
        help="Directory to search for identical bytes (default: file parent)",
    )
    parser.add_argument("--json", action="store_true", help="JSON only")
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"File not found: {args.pdf}", file=sys.stderr)
        return 1

    identity = file_identity(args.pdf, scan_dir=args.scan_dir)
    if args.json:
        print(json.dumps(identity, ensure_ascii=False, indent=2))
        return 0

    print(f"realpath: {identity['realpath']}")
    print(f"sha256: {identity['sha256']}")
    print(f"size: {identity['size']}")
    print(f"mtime: {identity['mtime']}")
    print(f"inode: {identity['inode']} nlink: {identity['nlink']}")
    if identity["same_bytes"]:
        print("same_bytes:")
        for extra in identity["same_bytes"]:
            print(f"  {extra}")
    else:
        print("same_bytes: (none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
