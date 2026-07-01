# Milo CLI plugins

The plugin catalog for the [Milo](https://github.com/milo-os) platform — a curated index of portable CLI plugins you can install and run through [`datumctl`](https://github.com/datum-cloud/datumctl).

Milo services ship their own command-line experiences as plugins. This catalog is how those plugins are discovered, versioned, and delivered to your machine: one place to browse what's available, install it for your OS and architecture, and keep it up to date — without cloning a repo or hunting for a release binary.

## Available plugins

| Name | Description |
|------|-------------|
| [inventory](plugins/inventory.yaml) | Browse and populate the Datum Cloud inventory graph (typed nodes and edges) |
| [ipam](plugins/ipam.yaml) | Manage IP address space (pools and prefixes) across the platform |

## Using this catalog

`datumctl` ships with the curated **datum** catalog out of the box. Register this catalog alongside it to make the Milo plugins installable too:

```sh
# Register the Milo catalog (a one-time trust decision)
datumctl plugin index add milo-os milo-os/cli-plugins

# Search and install across every registered catalog
datumctl plugin search ipam
datumctl plugin install ipam

# Or browse interactively
datumctl plugin browse
```

Once installed, a plugin runs as a first-class subcommand:

```sh
datumctl ipam pool list
```

`datumctl plugin list` shows what you have installed and which catalog each plugin came from, with a clear official vs. third-party badge so provenance is never ambiguous.

## Submitting a plugin

1. Add the `datumctl-plugin` topic to your plugin's GitHub repository.
2. Open a pull request adding `plugins/<your-plugin-name>.yaml`, following the [schema](schema/plugin-v1alpha1.json). That's the only file you edit.
3. CI validates every manifest: schema conformance, that each download URL resolves, and that each SHA256 matches the published archive. A weekly [health check](.github/workflows/catalog-health.yaml) re-verifies the whole catalog so a plugin's links can't rot unnoticed.
4. On merge, [`index.yaml`](index.yaml) — the file `datumctl` actually reads — is regenerated from `plugins/*.yaml` and committed automatically. You never edit it by hand. (To preview locally: `python3 scripts/generate_index.py`.)

## Plugin manifest format

```yaml
apiVersion: datumctl.datum.net/v1alpha1
kind: Plugin
metadata:
  name: my-plugin          # short name: datumctl plugin install my-plugin
spec:
  shortDescription: One-line description shown in datumctl plugin search
  homepage: https://github.com/milo-os/my-plugin
  version: v1.0.0
  platforms:
    - selector:
        matchLabels:
          os: linux
          arch: amd64
      uri: https://github.com/milo-os/my-plugin/releases/download/v1.0.0/milo-my-plugin_Linux_x86_64.tar.gz
      sha256: <lowercase hex sha256 of the archive>
```

### Binary naming

Plugins in this catalog use the portable **`milo-<name>`** binary convention (for example `milo-ipam`). `datumctl` recognizes both `milo-` and `datumctl-` prefixed plugins, so a single `milo-<name>` binary works as a `datumctl` subcommand and as a standalone tool on your `PATH`. The binary inside each archive must be named `milo-<name>` (or `milo-<name>.exe` on Windows).
