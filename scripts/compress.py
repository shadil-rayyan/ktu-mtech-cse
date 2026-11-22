#!/usr/bin/env python3
"""Lossless compression for files under public/academiadrive."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "public" / "academiadrive"
MANIFEST = Path(__file__).resolve().parents[1] / ".compress-manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    if MANIFEST.is_file():
        try:
            data = json.loads(MANIFEST.read_text())
            if isinstance(data, dict) and isinstance(data.get("files"), dict):
                return data
        except (OSError, ValueError):
            pass
    return {"version": 1, "files": {}}


def save_manifest(manifest: dict) -> None:
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def compress_pdf(src: Path) -> bool:
    tmp = src.with_suffix(".tmp.pdf")
    subprocess.run(
        [
            "gs", "-q", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            "-dNOPAUSE", "-dBATCH", "-dQUIET",
            "-dDownsampleColorImages=false",
            "-dDownsampleGrayImages=false",
            "-dDownsampleMonoImages=false",
            "-dAutoFilterColorImages=false",
            "-dColorImageFilter=/FlateEncode",
            "-dGrayImageFilter=/FlateEncode",
            "-dMonoImageFilter=/FlateEncode",
            "-dPassThroughJPEGImages=true",
            "-dPassThroughJPXImages=true",
            f"-sOutputFile={tmp}", str(src),
        ],
        check=True,
    )
    try:
        from pypdf import PdfReader
        a = len(PdfReader(str(src)).pages)
        b = len(PdfReader(str(tmp)).pages)
    except Exception:
        a = b = -1
    if a != b or a < 0:
        tmp.unlink(missing_ok=True)
        return False
    if tmp.stat().st_size < src.stat().st_size:
        shutil.move(str(tmp), str(src))
        return True
    tmp.unlink(missing_ok=True)
    return False


def compress_png(src: Path) -> bool:
    from PIL import Image
    tmp = src.with_suffix(".tmp.png")
    with Image.open(src) as im:
        im.save(tmp, optimize=True)
    if tmp.stat().st_size < src.stat().st_size:
        shutil.move(str(tmp), str(src))
        return True
    tmp.unlink(missing_ok=True)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Lossless compression for files under public/academiadrive.")
    parser.add_argument("--force", action="store_true", help="Reprocess files even if already recorded.")
    args = parser.parse_args()

    if not ROOT.is_dir():
        print("academiadrive not found", file=sys.stderr)
        return 1

    manifest = load_manifest()
    files_manifest = manifest.setdefault("files", {})

    saved = 0
    changed = 0
    total = 0
    present: set[str] = set()

    for src in sorted(ROOT.rglob("*")):
        if not src.is_file():
            continue
        if src.name.endswith(".tmp.pdf") or src.name.endswith(".tmp.png"):
            continue
        total += 1
        rel = src.relative_to(ROOT).as_posix()
        present.add(rel)
        before = src.stat().st_size
        before_hash = sha256_file(src)

        entry = files_manifest.get(rel)
        if not args.force and isinstance(entry, dict) and entry.get("sha256") == before_hash:
            print(f"skip {src} (already processed)")
            continue

        ext = src.suffix.lower()
        ok = False
        if ext == ".pdf":
            ok = compress_pdf(src)
        elif ext == ".png":
            ok = compress_png(src)

        after_hash = sha256_file(src)
        files_manifest[rel] = {"sha256": after_hash, "size": src.stat().st_size}

        if ok:
            changed += 1
            saved += before - src.stat().st_size
            print(f"compressed {src}: {before} -> {src.stat().st_size}")
        else:
            print(f"skip {src}")

    for rel in list(files_manifest):
        if rel not in present:
            del files_manifest[rel]

    save_manifest(manifest)
    print(f"done: {changed}/{total} files, saved {saved} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
