#!/usr/bin/env python3
"""Bind a CMSIS trace capture to its inputs using JSON on stdout; write no files."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
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

    state = {
        "version": 1,
        "target": args.target,
        "workspace": str(paths["workspace"]),
        "elf": str(paths["elf"]),
        "elf_sha256": digest(paths["elf"]),
        "csv": str(paths["csv"]),
        "raw": str(paths["raw"]),
        "sources": sources,
        "inputs": {str(paths[key]): digest(paths[key]) for key in (
            "source_profile", "runtime_profile", "run_description", "compile_commands")},
        "capture_started_ns": time.time_ns(),
    }
    print(json.dumps(state, indent=2))


def verify_inputs(state):
    if digest(state["elf"]) != state["elf_sha256"]:
        raise ValueError("ELF changed; build, regenerate and prepare a new capture")
    for source, expected in state["inputs"].items():
        if digest(source) != expected:
            raise ValueError(f"Capture input changed: {source}")
    active_file = Path(state["workspace"]) / ".vscode/cmsis.json"
    if active_file.is_file():
        active = json.loads(active_file.read_text()).get("activeTarget")
        if active and active != state["target"]:
            raise ValueError("Active target changed since capture preparation")


def verify(args):
    state = json.loads(args.state_json)
    if not isinstance(state, dict):
        raise ValueError("Capture state must be a JSON object")
    verify_inputs(state)
    files = [Path(state[key]) for key in ("raw", "csv")]
    deadline = time.monotonic() + args.timeout
    previous = None
    stable_since = time.monotonic()
    while time.monotonic() < deadline:
        try:
            sample = [(p.stat().st_size, p.stat().st_mtime_ns) for p in files]
        except FileNotFoundError:
            sample = None
        fresh = sample is not None and all(
            size > 0 and modified >= state["capture_started_ns"]
            for size, modified in sample)
        # The final CSV must have been decoded after the last RAW write.
        fresh = fresh and sample[1][1] >= sample[0][1]
        if not fresh or sample != previous:
            stable_since = time.monotonic()
        elif time.monotonic() - stable_since >= 1.0:
            break
        previous = sample
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
    verify_inputs(state)
    for key, source in zip(("raw", "csv"), files):
        state[f"{key}_sha256"] = digest(source)
    state["verified_ns"] = time.time_ns()
    state.update(raw_bytes=files[0].stat().st_size, rows=len(rows), pc_rows=pc_rows)
    print(json.dumps(state, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="Read capture inputs into JSON on stdout before starting debug")
    for name in ("target", "workspace", "elf", "csv", "raw", "source-profile",
                 "runtime-profile", "run-description", "compile-commands"):
        prepare_parser.add_argument("--" + name, required=True)
    verify_parser = commands.add_parser("verify", help="Wait for final conversion after debug has ended")
    verify_parser.add_argument("--state-json", required=True,
                               help="JSON returned by prepare; retained in memory, not a file")
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
