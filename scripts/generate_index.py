#!/usr/bin/env python3
"""Generate index.yaml from the per-plugin manifests in plugins/.

index.yaml is the single file datumctl reads to discover plugins, their
versions, and per-platform download locations. It is fully derived from
plugins/*.yaml, so it is regenerated deterministically here and checked for
drift in CI (`--check`) rather than hand-edited.

Usage:
  scripts/generate_index.py           # write index.yaml
  scripts/generate_index.py --check   # fail if index.yaml is out of date
"""
import difflib
import os
import sys

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR = os.path.join(REPO_ROOT, "plugins")
INDEX_PATH = os.path.join(REPO_ROOT, "index.yaml")

# Catalog identity header, surfaced in `datumctl plugin index list` and
# `datumctl plugin browse`, followed by one entry per plugin manifest.
HEADER = {
    "apiVersion": "datumctl.datum.net/v1alpha1",
    "kind": "PluginList",
    "name": "milo-os",
    "description": "Portable CLI plugins for the Milo platform",
    "owner": "milo-os",
    "homepage": "https://github.com/milo-os/cli-plugins",
}


def render() -> tuple[str, int]:
    index = dict(HEADER)
    index["items"] = []
    for filename in sorted(os.listdir(PLUGINS_DIR)):
        if not filename.endswith(".yaml"):
            continue
        with open(os.path.join(PLUGINS_DIR, filename)) as fh:
            index["items"].append(yaml.safe_load(fh))
    text = yaml.dump(
        index, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    return text, len(index["items"])


def main() -> None:
    expected, count = render()

    if "--check" in sys.argv[1:]:
        current = ""
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH) as fh:
                current = fh.read()
        if current != expected:
            print(
                "index.yaml is out of sync with plugins/.\n"
                "Run `python3 scripts/generate_index.py` and commit the result.\n",
                file=sys.stderr,
            )
            diff = difflib.unified_diff(
                current.splitlines(),
                expected.splitlines(),
                fromfile="index.yaml (committed)",
                tofile="index.yaml (expected)",
                lineterm="",
            )
            print("\n".join(diff), file=sys.stderr)
            sys.exit(1)
        print(f"index.yaml is in sync ({count} plugin(s)).")
        return

    with open(INDEX_PATH, "w") as fh:
        fh.write(expected)
    print(f"Wrote index.yaml ({count} plugin(s)).")


if __name__ == "__main__":
    main()
