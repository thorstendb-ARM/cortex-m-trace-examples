#!/usr/bin/env python3
"""Bind one CMSIS trace capture to its ELF, profiles, sources and fresh CSV."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(args):
    paths = {key: Path(getattr(args, key)).resolve() for key in (
        "elf", "csv", "raw", "source_profile", "runtime_profile",
        "run_description", "compile_commands", "workspace")}
    for key in ("elf", "source_profile", "runtime_profile", "run_description",
                "compile_commands"):
        if not paths[key].is_file():
            raise ValueError(f"Missing {key}: {paths[key]}")
    if paths["elf"].read_bytes()[:4] != b"\x7fELF":
        raise ValueError("Selected image is not an ELF file")
    active_file = paths["workspace"] / ".vscode/cmsis.json"
    if active_file.is_file():
        active = json.loads(active_file.read_text()).get("activeTarget")
        if active and active != args.target:
            raise ValueError(f"Selected target is {active!r}, not {args.target!r}")
    sources = {}
    for entry in json.loads(paths["compile_commands"].read_text()):
        source = Path(entry["file"])
        if not source.is_absolute():
            source = Path(entry["directory"]) / source
        source = source.resolve()
        sources[str(source)] = digest(source)
    if not sources:
        raise ValueError("The compilation database has no sources")

    parent = paths["csv"].parent / "captures"
    parent.mkdir(parents=True, exist_ok=True)
    capture_dir = Path(tempfile.mkdtemp(prefix="stack-magic-", dir=parent))
    snapshot_elf = capture_dir / paths["elf"].name
    shutil.copy2(paths["elf"], snapshot_elf)
    for key in ("source_profile", "runtime_profile"):
        shutil.copy2(paths[key], capture_dir / paths[key].name)
    # Avoid *.cbuild-run.yml: CMSIS build tools would discover a duplicate context.
    shutil.copy2(paths["run_description"], capture_dir / "run-description.snapshot.yml")
    manifest = {
        "version": 1,
        "target": args.target,
        "workspace": str(paths["workspace"]),
        "elf": str(snapshot_elf),
        "elf_original": str(paths["elf"]),
        "elf_sha256": digest(snapshot_elf),
        "csv": str(paths["csv"]),
        "raw": str(paths["raw"]),
        "sources": sources,
        "inputs": {str(paths[key]): digest(paths[key]) for key in (
            "source_profile", "runtime_profile", "run_description")},
        "capture_started_ns": time.time_ns(),
    }
    output = capture_dir / "manifest.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"manifest": str(output), **manifest}, indent=2))


def verify_inputs(manifest):
    for key in ("elf", "elf_original"):
        if digest(manifest[key]) != manifest["elf_sha256"]:
            raise ValueError("ELF changed; build, regenerate and prepare a new capture")
    for source, expected in manifest["inputs"].items():
        if digest(source) != expected:
            raise ValueError(f"Capture input changed: {source}")
    active_file = Path(manifest["workspace"]) / ".vscode/cmsis.json"
    if active_file.is_file():
        active = json.loads(active_file.read_text()).get("activeTarget")
        if active and active != manifest["target"]:
            raise ValueError("Active target changed since capture preparation")


def verify(args):
    path = Path(args.manifest).resolve()
    manifest = json.loads(path.read_text())
    verify_inputs(manifest)
    files = [Path(manifest[key]) for key in ("raw", "csv")]
    deadline = time.monotonic() + args.timeout
    previous = None
    stable_since = time.monotonic()
    while time.monotonic() < deadline:
        try:
            state = [(p.stat().st_size, p.stat().st_mtime_ns) for p in files]
        except FileNotFoundError:
            state = None
        fresh = state is not None and all(
            size > 0 and modified >= manifest["capture_started_ns"]
            for size, modified in state)
        # The final CSV must have been decoded after the last RAW write.
        fresh = fresh and state[1][1] >= state[0][1]
        if not fresh or state != previous:
            stable_since = time.monotonic()
        elif time.monotonic() - stable_since >= 1.0:
            break
        previous = state
        time.sleep(0.2)
    else:
        raise ValueError("No fresh, stable RAW/CSV pair; await conversion or decode the final RAW with ctrace")
    with files[1].open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "pc" not in reader.fieldnames:
            raise ValueError("CSV has no pc column")
        rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        raise ValueError("CSV row length differs from its header")
    pc_rows = sum(bool(row.get("pc", "").strip()) for row in rows)
    if not pc_rows:
        raise ValueError("CSV contains no PC records; do not claim a successful magic-word capture")
    # The selected context may change while waiting for asynchronous conversion.
    verify_inputs(manifest)
    for key, source in zip(("raw", "csv"), files):
        shutil.copy2(source, path.parent / source.name)
        manifest[f"{key}_sha256"] = digest(source)
    manifest["verified_ns"] = time.time_ns()
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"target": manifest["target"], "raw_bytes": files[0].stat().st_size,
                      "rows": len(rows), "pc_rows": pc_rows,
                      "manifest": str(path), "elf": manifest["elf"],
                      "csv": manifest["csv"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="Snapshot capture inputs before starting debug")
    for name in ("target", "workspace", "elf", "csv", "raw", "source-profile",
                 "runtime-profile", "run-description", "compile-commands"):
        prepare_parser.add_argument("--" + name, required=True)
    verify_parser = commands.add_parser("verify", help="Wait for final conversion after debug has ended")
    verify_parser.add_argument("--manifest", required=True)
    verify_parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()
    try:
        (prepare if args.command == "prepare" else verify)(args)
    except (OSError, ValueError, KeyError, csv.Error) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
