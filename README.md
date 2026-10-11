# AstraeaWave
Mock IMAP server in Swift

## Design documentation

The [design specification](doc/design/design.md) is generated from the CSV catalogs
in [doc/design-meta/examples](doc/design-meta/examples). Edit these source files to
evolve the specification; [app.cue](doc/design-meta/app.cue) assembles the report.

AI coding agents can start with the [task search entry point](doc/design-meta/AGENTS.md).
See the [source search convention](doc/design-meta/README.md) for concept-based
`rg` retrieval and CSV editing rules. With Python 3 and `flyb` installed,
validate the catalogs and regenerate from the repository root:

```sh
sh scripts/generate_design.sh
```

The design currently proposes Kotlin/JVM with GreenMail; the implementation
language remains an open decision recorded in the feature catalog.
