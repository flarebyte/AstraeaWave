# AstraeaWave
Mock IMAP server in Swift

## Design documentation

The [design specification](doc/design/design.md) is generated from the CSV catalogs
in [doc/design-meta/examples](doc/design-meta/examples). Edit these source files to
evolve the specification; [app.cue](doc/design-meta/app.cue) assembles the report.

With `flyb` installed, regenerate from the repository root:

```sh
flyb validate --config doc/design-meta
flyb generate markdown --config doc/design-meta
```

The design currently proposes Kotlin/JVM with GreenMail; the implementation
language remains an open decision recorded in the feature catalog.
