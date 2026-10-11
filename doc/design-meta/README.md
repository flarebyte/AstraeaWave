# Selective source retrieval

`examples/concepts.csv` is the canonical concept registry. Each stable lowercase
dot-separated `id` names a semantic group, with a concise description and an
empty parent for roots or the immediate registered parent for children. Reuse
these IDs across catalogs; add a concept only when it improves selective retrieval.

`feature.csv`, `cli-command.csv`, and `technology.csv` append a `concept` column
for each record's primary topic. A concept groups related requirements, commands,
and dependencies; it does not replace the record's `id` or its relationships.
Secondary topics remain discoverable through the existing `feature_refs` and
prose. `technology.csv` also appends optional `tags` for capability keywords such
as `mime`, `http`, and `json`. Tags are lowercase words (hyphens allowed), unique
within a cell, comma-separated without spaces, and quoted as one CSV cell.
Use the existing scope, kind, area, and dependency columns for their own filters.

`network-profile.csv` stays unchanged: its eight rows already cover one topic,
`network.profiles`, and its profile and direction columns provide useful filters.
The registry itself has only `id,description,parent`.

Keep headers unquoted and data cells quoted, escape embedded quotes as `""`,
and keep every record on one physical line. Standard CSV readers retain embedded
commas correctly; use a CSV parser when selecting columns rather than splitting
lines on commas. Record IDs are unique within each catalog, not across catalogs
(existing feature and CLI IDs can overlap). Concept IDs are unique in the registry.

From the repository root, first discover a concept, then retrieve its rows:

```sh
# Locate the network branch in the registry (root and descendants).
rg -n '^"network(\.[^"]+)?",' doc/design-meta/examples/concepts.csv

# Retrieve the primary network profiles topic across annotated catalogs.
rg -n -F ',"network.profiles"' doc/design-meta/examples/{feature,cli-command,technology}.csv

# Retrieve a whole concept branch, plus the intentionally unannotated catalog.
rg -n ',"network\.[^"]+"(,|$)' doc/design-meta/examples/{feature,cli-command,technology}.csv
cat doc/design-meta/examples/network-profile.csv

# Find dependencies with the exact MIME tag (including multi-tag cells).
rg -n ',"([^",]+,)*mime(,[^",]+)*"$' doc/design-meta/examples/technology.csv

# Follow a requirement's existing ID/references, including secondary topics.
rg -n -F 'lifecycle.reset' doc/design-meta/examples/*.csv

# grep supports the same fixed-string concept lookup.
grep -nF ',"fixture.validation"' doc/design-meta/examples/*.csv
```

These searches select whole source records; inspect the header when interpreting
cells. Exact quoted concept searches avoid matching descendant concepts by
accident. Hierarchical membership uses the registry's parent relation, while
`feature_refs` retains the existing semicolon-separated requirement relationships.

`app.cue` is the report manifest. Its CSV table renderer includes the appended
columns automatically; the source navigation section renders the registry and
links to this convention. Regenerate with validation before any Markdown output is written:

```sh
sh scripts/generate_design.sh
```

The wrapper requires Python 3 and `flyb` (override the executable with `FLYB`).
The CSV validator checks required catalogs and columns, quoting, row widths,
one-line records, catalog ID uniqueness, registry descriptions and parents,
concept references, tag syntax, and existing feature references. It also validates
any additional CSV catalogs in `examples/`; each must have an `id` column.
Run it independently or run its regression tests:

```sh
python3 scripts/validate_design_csv.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```
