"""Regression tests for invalid source data and the generation validation gate."""

import csv
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from validate_design_csv import DEFAULT_EXAMPLES, validate


class CatalogValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.examples = Path(self.temp.name) / "examples"
        shutil.copytree(DEFAULT_EXAMPLES, self.examples)

    def change(self, name, mutate):
        path = self.examples / name
        with path.open(newline="") as source:
            reader = csv.DictReader(source)
            fields = reader.fieldnames
            rows = list(reader)
        mutate(rows)
        with path.open("w", newline="") as target:
            writer = csv.DictWriter(target, fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def assert_error(self, text):
        self.assertTrue(any(text in error for error in validate(self.examples)), text)

    def test_repository_catalogs_are_valid(self):
        self.assertEqual(validate(self.examples), [])

    def test_unknown_and_empty_concepts(self):
        for value in ("missing.topic", ""):
            with self.subTest(value=value):
                self.change("feature.csv", lambda rows: rows[0].update(concept=value))
                self.assert_error("unknown concept")

    def test_duplicate_ids_in_catalog_and_registry(self):
        for name in ("cli-command.csv", "concepts.csv"):
            with self.subTest(name=name):
                self.change(name, lambda rows: rows.append(rows[0].copy()))
                self.assert_error("duplicate id")

    def test_invalid_concept_identifier(self):
        self.change("concepts.csv", lambda rows: rows[0].update(id="Product..Scope"))
        self.assert_error("invalid id")

    def test_missing_parent(self):
        self.change("concepts.csv", lambda rows: rows.remove(next(row for row in rows if row["id"] == "fixture")))
        self.assert_error("unknown parent 'fixture'")

    def test_wrong_parent_and_self_cycle(self):
        for parent in ("network", "fixture.model"):
            with self.subTest(parent=parent):
                self.change("concepts.csv", lambda rows: next(row for row in rows if row["id"] == "fixture.model").update(parent=parent))
                self.assert_error("immediate hierarchical parent")

    def test_missing_description(self):
        self.change("concepts.csv", lambda rows: rows[0].update(description=" "))
        self.assert_error("concept description is required")

    def test_unknown_feature_reference(self):
        self.change("network-profile.csv", lambda rows: rows[0].update(feature_refs="network.profiles; missing.feature"))
        self.assert_error("unknown feature reference 'missing.feature'")

    def test_invalid_tags(self):
        for value in ("mime, mime", "mime,mime", "mime,", "MIME"):
            with self.subTest(value=value):
                self.change("technology.csv", lambda rows: rows[0].update(tags=value))
                self.assert_error("tags must be unique lowercase keywords")

    def test_multiline_cell(self):
        self.change("feature.csv", lambda rows: rows[0].update(specification="first\nsecond"))
        self.assert_error("one record per physical line")

    def test_bad_quoting_and_row_width(self):
        path = self.examples / "extra.csv"
        for record, expected in (
            ('"unterminated', "invalid CSV"),
            ('bad"quote', "invalid CSV"),
            ('"closed"junk', "invalid CSV"),
            ('"extra","cell"', "expected 1 cells, found 2"),
            ('', "invalid CSV"),
        ):
            with self.subTest(record=record):
                path.write_text("id\n" + record + "\n")
                self.assert_error(expected)

    def test_duplicate_header(self):
        (self.examples / "extra.csv").write_text('id,id\n"one","two"\n')
        self.assert_error("header names must be nonempty, unique")

    def test_missing_column_and_catalog(self):
        path = self.examples / "feature.csv"
        path.write_text('id\n"one"\n')
        self.assert_error("missing columns")
        path.unlink()
        self.assert_error("required catalog is missing")

    def test_new_catalog_concept_is_validated(self):
        (self.examples / "extra.csv").write_text('id,concept\n"one","missing.topic"\n')
        self.assert_error("unknown concept 'missing.topic'")

    def test_cli_failure_is_nonzero_with_location(self):
        self.change("feature.csv", lambda rows: rows[0].update(concept="missing.topic"))
        result = subprocess.run(
            ["python3", str(Path(__file__).with_name("validate_design_csv.py")), "--examples-dir", str(self.examples)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("feature.csv:2: unknown concept", result.stderr)

    def test_generation_stops_before_flyb_on_invalid_sources(self):
        root = Path(self.temp.name) / "repo"
        scripts = root / "scripts"
        scripts.mkdir(parents=True)
        for name in ("generate_design.sh", "validate_design_csv.py"):
            shutil.copyfile(Path(__file__).with_name(name), scripts / name)
        target = root / "doc/design-meta/examples"
        target.parent.mkdir(parents=True)
        shutil.copytree(self.examples, target)
        (target / "concepts.csv").write_text("id,description,parent\n")
        marker = root / "flyb-was-called"
        fake = root / "flyb"
        fake.write_text('#!/bin/sh\ntouch "$(dirname "$0")/flyb-was-called"\n')
        fake.chmod(0o755)
        result = subprocess.run(
            ["sh", str(scripts / "generate_design.sh")],
            env={**os.environ, "FLYB": str(fake)}, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown concept", result.stderr)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
