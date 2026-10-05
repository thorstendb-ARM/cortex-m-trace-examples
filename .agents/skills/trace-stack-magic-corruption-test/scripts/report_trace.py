#!/usr/bin/env python3
"""Write a Markdown source report for a completed ctrace CSV; keep inputs intact."""

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile


ADDRESS = re.compile(r"^(?:0[xX])?[0-9a-fA-F]+$")
LOCATION = re.compile(r"^(.*):(\d+|\?)(?: \(discriminator \d+\))?$")
HASH = re.compile(r"[0-9a-fA-F]{64}")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_path(name, root):
    path = Path(name)
    return (path if path.is_absolute() else root / path).resolve()


def relative_name(path, root):
    return Path(os.path.relpath(path, root)).as_posix()


def read_manifest(path, root):
    if path is None:
        return {}, {}, set(), None
    original = path.read_bytes()
    manifest = json.loads(original)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), dict):
        raise ValueError("Manifest requires a sources path/hash object")
    if not isinstance(manifest.get("elf_sha256"), str) or not HASH.fullmatch(manifest["elf_sha256"]):
        raise ValueError("Manifest requires a valid elf_sha256")
    sources = {}
    for name, digest in manifest["sources"].items():
        if not isinstance(digest, str) or not HASH.fullmatch(digest):
            raise ValueError(f"Invalid source SHA-256 in manifest: {name}")
        sources[local_path(name, root)] = digest.lower()
    protected = set(sources)
    protected.update(local_path(name, root) for name in manifest.get("inputs", {}))
    for key, value in manifest.items():
        if isinstance(value, str) and (Path(value).is_absolute() or key in ("elf", "elf_original", "csv", "raw", "profile")):
            protected.add(local_path(value, root))
    return manifest, sources, protected, original


def check_output(output, protected):
    if output.suffix.casefold() != ".md":
        raise ValueError("Report output must have a .md extension")
    resolved = output.resolve()
    for path in protected:
        if resolved == path.resolve() or (output.exists() and path.exists() and output.samefile(path)):
            raise ValueError(f"Report output aliases an input: {path}")


def inline_code(value):
    # Escape embedded newlines in names; multiline values use fenced blocks below.
    value = str(value).replace("\r", "\\r").replace("\n", "\\n")
    length = max((len(match) for match in re.findall(r"`+", value)), default=0) + 1
    fence = "`" * length
    padding = " " if value.startswith(("`", " ")) or value.endswith(("`", " ")) else ""
    return fence + padding + value + padding + fence


def fenced(value, language="text"):
    length = max(3, max((len(match) for match in re.findall(r"`+", value)), default=0) + 1)
    fence = "`" * length
    return f"{fence}{language}\n{value}\n{fence}"


def resolve_addresses(tool, elf, addresses):
    """Parse address/function/location pairs, preserving all inline frames."""
    if not addresses:
        return {}
    result = subprocess.run(
        [str(tool), "-a", "-f", "-C", "-i", "-e", str(elf)],
        input="".join(f"0x{address:x}\n" for address in addresses),
        text=True, encoding="utf-8", errors="replace", capture_output=True,
        check=False, timeout=60,
    )
    if result.returncode:
        raise ValueError(f"addr2line failed ({result.returncode}): {result.stderr.strip()}")
    blocks, seen, current = {}, [], None
    for line in result.stdout.splitlines():
        if re.fullmatch(r"0[xX][0-9a-fA-F]+", line):
            current = int(line, 16)
            if current in blocks:
                raise ValueError("addr2line returned a duplicate address block")
            blocks[current] = []
            seen.append(current)
        elif current is None:
            raise ValueError("addr2line output has no initial address marker")
        else:
            blocks[current].append(line)
    if seen != addresses:
        raise ValueError("addr2line did not return the requested addresses in order")
    for address, lines in blocks.items():
        if not lines or len(lines) % 2:
            raise ValueError(f"Incomplete addr2line frames for 0x{address:x}")
        blocks[address] = list(zip(lines[0::2], lines[1::2]))
    return blocks


def source_details(location, root, hashes, cache, warnings):
    match = LOCATION.fullmatch(location)
    if not match or match[1] == "??" or match[2] in ("?", "0"):
        return None, None, "Source location unresolved."
    path = local_path(match[1], root)
    number = int(match[2])
    label = f"{relative_name(path, root)}:{number}"
    if path not in cache:
        if path not in hashes:
            cache[path] = (None, "Source hash unavailable in capture manifest; text omitted.")
        else:
            try:
                raw = path.read_bytes()
                if sha256(raw) != hashes[path]:
                    cache[path] = (None, "Source changed since capture; text omitted.")
                else:
                    cache[path] = (raw.decode("utf-8").splitlines(), None)
            except (OSError, UnicodeError):
                cache[path] = (None, "Source unavailable; text omitted.")
    lines, error = cache[path]
    if not error and number > len(lines):
        error = "Source line outside file; text omitted."
    if error:
        warnings.append(f"{label}: {error}")
        return label, None, error
    return label, lines[number - 1].strip(), None


def trace_fields(header, row, pc_index):
    """Retain original nonempty values, including decoder notes and extra columns."""
    fields = [(header[i] if i < len(header) else f"column {i + 1}", value)
              for i, value in enumerate(row) if value != "" and i != pc_index]
    if pc_index is not None and pc_index < len(row) and row[pc_index] != "":
        fields.insert(0, (header[pc_index], row[pc_index]))
    compact, multiline = [], []
    for name, value in fields:
        label = inline_code(name)
        if "\n" in value or "\r" in value:
            multiline.extend([f"CSV {label}:", fenced(value)])
        else:
            compact.append(f"{label}: {inline_code(value)}")
    return ([" · ".join(compact)] if compact else []) + multiline


def report(args):
    csv_path = args.csv.resolve()
    elf = args.elf.resolve()
    root = args.source_root.resolve()
    output = (args.output or args.csv.with_suffix(".md")).absolute()
    manifest, hashes, protected, manifest_bytes = read_manifest(args.source_manifest, root)
    protected.update((csv_path, elf, args.addr2line.resolve()))
    if args.source_manifest:
        protected.add(args.source_manifest.resolve())
    check_output(output, protected)

    manifest_elf = manifest.get("elf_sha256", "").lower() or None
    expected = args.elf_sha256.lower() if args.elf_sha256 else manifest_elf
    if expected is not None and not HASH.fullmatch(expected):
        raise ValueError("ELF SHA-256 must contain 64 hexadecimal characters")
    if manifest_elf is not None and expected != manifest_elf:
        raise ValueError("--elf-sha256 disagrees with capture manifest")
    elf_hash = file_hash(elf)
    if expected is not None and elf_hash != expected:
        raise ValueError("ELF differs from capture SHA-256; report left unchanged")
    csv_bytes = csv_path.read_bytes()
    csv_hash = sha256(csv_bytes)
    if manifest.get("csv_sha256") is not None and csv_hash != manifest["csv_sha256"]:
        raise ValueError("CSV differs from capture SHA-256; use the archived original CSV")
    rows = list(csv.reader(io.StringIO(csv_bytes.decode("utf-8-sig"), newline=""), strict=True))
    if not rows or not rows[0]:
        raise ValueError("CSV has no header")
    header, records = rows[0], rows[1:]
    pc_columns = [i for i, name in enumerate(header) if name.casefold() == "pc"]
    if len(pc_columns) > 1:
        raise ValueError("CSV has multiple PC columns")
    pc_index = pc_columns[0] if pc_columns else None
    raw_pcs = [row[pc_index].strip() if pc_index is not None and pc_index < len(row) else "" for row in records]
    parsed = [int(raw, 16) if raw and ADDRESS.fullmatch(raw) else None for raw in raw_pcs]
    addresses = list(dict.fromkeys(address for address in parsed if address is not None))
    resolved = resolve_addresses(args.addr2line, elf, addresses)

    parts = ["# Stack magic trace", f"CSV: {inline_code(relative_name(csv_path, root))}"]
    if isinstance(manifest.get("target"), str):
        parts.append(f"Target: {inline_code(manifest['target'])}")
    cache, warnings, unresolved = {}, [], 0
    for index, (row, raw_pc, address) in enumerate(zip(records, raw_pcs, parsed), start=1):
        parts.append(f"## Entry {index}")
        located = False
        if not raw_pc:
            parts.append("Status: No PC recorded; source lookup not applicable.")
        elif address is None:
            parts.append("Status: Invalid PC; source unresolved.")
        else:
            frames = resolved[address]
            for frame_index, (function, location) in enumerate(frames):
                if frame_index:
                    parts.append(f"**Inline caller {frame_index}** ({inline_code(function)})")
                label, source, error = source_details(location, root, hashes, cache, warnings)
                located = located or label is not None
                if source is not None:
                    parts.append(fenced(source, "c"))
                else:
                    parts.append(f"Status: {error}")
                if label is not None:
                    parts.append(f"Location: {inline_code(label)}")
        if raw_pc and not located:
            unresolved += 1
        parts.extend(trace_fields(header, row, pc_index))
    updated = ("\n\n".join(parts) + "\n").encode("utf-8")

    def recheck_inputs():
        check_output(output, protected)
        if csv_path.read_bytes() != csv_bytes:
            raise ValueError("CSV changed during reporting; stop capture/conversion first")
        if file_hash(elf) != elf_hash:
            raise ValueError("ELF changed during reporting; report left unchanged")
        if args.source_manifest and args.source_manifest.read_bytes() != manifest_bytes:
            raise ValueError("Capture manifest changed during reporting; report left unchanged")

    recheck_inputs()
    changed = not output.exists() or output.read_bytes() != updated
    if changed:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(updated)
                handle.flush()
                os.fsync(handle.fileno())
            if output.exists():
                temporary.chmod(stat.S_IMODE(output.stat().st_mode))
            recheck_inputs()
            os.replace(temporary, output)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    print(json.dumps({
        "rows": len(records), "sections": len(records),
        "pc_rows": sum(bool(raw) for raw in raw_pcs), "unique_pcs": len(addresses),
        "unresolved_rows": unresolved, "source_warnings": list(dict.fromkeys(warnings)),
        "report": str(output), "csv_sha256": csv_hash, "elf_sha256": elf_hash,
        "changed": changed,
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--addr2line", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--elf-sha256")
    parser.add_argument("--output", type=Path)
    try:
        report(parser.parse_args())
    except (OSError, ValueError, csv.Error, subprocess.SubprocessError) as error:
        print(f"report_trace: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
