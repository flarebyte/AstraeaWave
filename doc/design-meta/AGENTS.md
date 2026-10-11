# Task-focused agent entry point

Start here when implementing or changing behavior described by this specification.
The CSVs in `examples/` are the editable design sources; `../design/design.md` is
generated. Retrieve the relevant records before opening whole catalogs or the
generated report. Commands below run from the repository root.

1. Choose the task's primary concept using the table below. Confirm its meaning
   in [examples/concepts.csv](examples/concepts.csv), the canonical registry.
2. Read catalog headers, then search the quoted concept across the feature,
   command, and technology catalogs. Read the matched requirements, acceptance
   criteria, open questions, command effects, and dependency notes.
3. Follow the selected records' `feature_refs` to their feature records. Search
   relevant feature IDs across catalogs to find secondary relationships that a
   primary-concept filter omits. Expand to adjacent concepts only when those
   records identify a dependency or constraint.
4. Locate implementation files with `rg --files`, then search relevant symbols
   within those files. Concept IDs organize design records; they are not assumed
   to appear in implementation code. This repository currently contains design
   sources and documentation tooling, with no mail-server implementation.
5. Stop expanding when the task's behavior, constraints, dependencies, and open
   questions are covered. Cite source paths and record IDs in implementation
   notes; preserve distinctions between proposed defaults and settled behavior.

| Task | Start with concepts | Expand when relevant |
| --- | --- | --- |
| Fixture layout, accounts, MIME, metadata | `fixture.model`, `fixture.source` | `fixture.validation`, `integration` |
| Load, replace, delete, reset | `lifecycle.accounts` | `fixture.source`, `fixture.model`, `lifecycle.control` |
| Startup, readiness, shutdown | `lifecycle.server` | `deployment`, `lifecycle.control` |
| CLI help, inventory, connection details, JSON | `cli` | The operation's lifecycle or network concept |
| Docker, Podman, listener configuration | `deployment.container`, `deployment` | `lifecycle.server`, `network.routing` for proxy deployments |
| Network faults and restoration | `network.profiles` | `network.routing`, `network.control`; also `examples/network-profile.csv` |
| Runtime, dependencies, build, tests | `tooling.runtime`, `tooling.build`, `tooling.testing` | `integration`, or the capability's concept/tag |
| Specification generation or scope | `tooling.docs`, `product` | `app.cue`, [README.md](README.md) |

For example, retrieve reset behavior and its relationships:

```sh
# Discover the relevant branch without reading the full specification.
rg -n '^"lifecycle(\.[^"]+)?",' doc/design-meta/examples/concepts.csv

# Read headers and primary account lifecycle records.
head -n 1 doc/design-meta/examples/{feature,cli-command,technology}.csv
rg -n -F ',"lifecycle.accounts"' doc/design-meta/examples/{feature,cli-command,technology}.csv

# Follow a specific feature ID and find references in other catalogs.
rg -n '^"lifecycle.reset",' doc/design-meta/examples/feature.csv
rg -n -F 'lifecycle.reset' doc/design-meta/examples/{cli-command,technology,network-profile}.csv

# Retrieve baseline constraints when implementing reset or replacement.
rg -n -F ',"fixture.source"' doc/design-meta/examples/{feature,cli-command,technology}.csv

# Discover code paths, excluding generated documentation and CSV catalogs.
rg --files -g '!doc/design/**' -g '!doc/design-meta/examples/**'

# Search code for related terms; narrow to discovered paths as code grows.
rg -n -g '*.kt' -g '*.swift' -g '*.py' -g '*.sh' 'reset|baseline|UIDVALIDITY' .
```

An empty code search can mean the behavior has not been implemented; check the
file inventory before treating it as a search failure. Use `grep -nF` for the
fixed-string lookups if `rg` is unavailable. Read [README.md](README.md) for
branch searches, exact tag filters, quoting rules, and CSV parsing guidance.

When editing design sources, reuse registered concepts, retain existing record
IDs and feature relationships, and keep each CSV record on one physical line.
Update `app.cue` when adding a catalog to the report. Validate and regenerate:

```sh
sh scripts/generate_design.sh
```

When changing the CSV validator or generation gate, also run:

```sh
python3 -B -m unittest discover -s scripts -p 'test_*.py'
```
