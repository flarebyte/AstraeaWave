#!/usr/bin/env python3
"""Validate design CSV catalogs using only the Python standard library."""

import argparse
import csv
from pathlib import Path
import re
import sys


DEFAULT_EXAMPLES = Path(__file__).resolve().parents[1] / "doc/design-meta/examples"
REQUIRED = {
    "concepts.csv": "id,description,parent",
    "feature.csv": "id,area,feature,scope,specification,acceptance_criteria,open_questions,concept",
    "cli-command.csv": "id,kind,command,scope,purpose,arguments_and_options,example,requires_running_server,expected_behavior,feature_refs,design_notes,concept",
    "technology.csv": "id,area,technology,role,requirement,dependency_kind,artifact_or_tool,version_policy,rationale,integration_notes,feature_refs,source_url,concept",
    "network-profile.csv": "id,profile,scope,default_parameters,allowed_overrides,direction,toxiproxy_mapping,behavior,restoration,validation_and_limits,feature_refs,source_url",
}
IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)*\Z")
KEYWORD = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
# Unlike csv.reader(strict=True), this also rejects quotes inside unquoted cells.
CELL = r'(?:[^,"\r\n]*|"(?:[^"\r\n]|"")*")'
RECORD = re.compile(CELL + r"(?:," + CELL + r")*\Z")


def validate(examples):
    errors = []
    catalogs = {}

    def fail(path, line, message):
        errors.append(f"{path.name}:{line}: {message}")

    for name in REQUIRED:
        if not (examples / name).is_file():
            fail(examples / name, 1, "required catalog is missing")
    for path in sorted(examples.glob("*.csv")):
        try:
            with path.open(encoding="utf-8", newline="") as source:
                lines = source.read().splitlines()
        except (OSError, UnicodeError) as exc:
            fail(path, 1, str(exc))
            continue
        parsed = []
        for number, line in enumerate(lines, 1):
            if not line or not RECORD.fullmatch(line):
                fail(path, number, "invalid CSV; use one record per physical line and escape quotes as double quotes")
                parsed.append(None)
                continue
            try:
                parsed.append(next(csv.reader([line], strict=True)))
            except csv.Error as exc:
                fail(path, number, f"invalid CSV: {exc}")
                parsed.append(None)
        if not parsed or parsed[0] is None:
            fail(path, 1, "missing or invalid header")
            continue
        header = parsed[0]
        if any(not field or field != field.strip() for field in header) or len(set(header)) != len(header):
            fail(path, 1, "header names must be nonempty, unique, and trimmed")
            continue
        required = REQUIRED.get(path.name, "id").split(",")
        if not set(required).issubset(header):
            fail(path, 1, "missing columns: " + ", ".join(sorted(set(required) - set(header))))
            continue
        if path.name == "concepts.csv" and header != ["id", "description", "parent"]:
            fail(path, 1, "registry columns must be id,description,parent")
        rows = []
        seen = set()
        for number, cells in enumerate(parsed[1:], 2):
            if cells is None:
                continue
            if len(cells) != len(header):
                fail(path, number, f"expected {len(header)} cells, found {len(cells)}")
                continue
            row = dict(zip(header, cells))
            identifier = row["id"]
            if not IDENTIFIER.fullmatch(identifier):
                fail(path, number, f"invalid id {identifier!r}")
            if identifier in seen:
                fail(path, number, f"duplicate id {identifier!r}")
            seen.add(identifier)
            if row.get("tags"):
                tags = row["tags"].split(",")
                if any(not KEYWORD.fullmatch(tag) for tag in tags) or len(tags) != len(set(tags)):
                    fail(path, number, "tags must be unique lowercase keywords separated by commas without spaces")
            rows.append((number, row))
        catalogs[path.name] = rows

    registry = {row["id"]: row for _, row in catalogs.get("concepts.csv", [])}
    for number, row in catalogs.get("concepts.csv", []):
        if not row["description"].strip():
            fail(examples / "concepts.csv", number, "concept description is required")
        parent = row["parent"]
        expected_parent = row["id"].rsplit(".", 1)[0] if "." in row["id"] else ""
        if parent != expected_parent:
            fail(examples / "concepts.csv", number, f"parent must be {expected_parent!r} (immediate hierarchical parent)")
        if parent and parent not in registry:
            fail(examples / "concepts.csv", number, f"unknown parent {parent!r}")
    feature_ids = {row["id"] for _, row in catalogs.get("feature.csv", [])}
    for name, rows in catalogs.items():
        for number, row in rows:
            if "concept" in row and row["concept"] not in registry:
                fail(examples / name, number, f"unknown concept {row['concept']!r}")
            for reference in row.get("feature_refs", "").split(";"):
                if reference.strip() and reference.strip() not in feature_ids:
                    fail(examples / name, number, f"unknown feature reference {reference.strip()!r}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples-dir", type=Path, default=DEFAULT_EXAMPLES)
    args = parser.parse_args()
    errors = validate(args.examples_dir)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Design CSV validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
