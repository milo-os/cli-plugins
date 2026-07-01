#!/usr/bin/env python3
"""Validate plugin manifests and verify their published release assets.

For each manifest (all of plugins/*.yaml by default, or the paths passed as
arguments) this:
  * validates it against schema/plugin-v1alpha1.json,
  * confirms every platform download URL resolves, and
  * downloads each archive and confirms its sha256 matches the manifest.

This is the check that keeps the catalog installable: a wrong checksum or a
deleted/retagged release asset fails here, in CI, rather than in a user's
`datumctl plugin install`.

Usage:
  scripts/verify_manifests.py                 # every plugins/*.yaml
  scripts/verify_manifests.py plugins/ipam.yaml ...
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

import yaml
from jsonschema import Draft7Validator, FormatChecker

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(REPO_ROOT, "schema", "plugin-v1alpha1.json")
PLUGINS_DIR = os.path.join(REPO_ROOT, "plugins")


def verify(path: str, validator: Draft7Validator) -> bool:
    print(f"== {os.path.relpath(path, REPO_ROOT)}")
    with open(path) as fh:
        manifest = yaml.safe_load(fh)

    errors = sorted(validator.iter_errors(manifest), key=lambda e: list(e.path))
    if errors:
        for e in errors:
            loc = "/".join(str(p) for p in e.path) or "(root)"
            print(f"  SCHEMA ERROR at {loc}: {e.message}", file=sys.stderr)
        return False
    print("  schema OK")

    ok = True
    for platform in manifest["spec"]["platforms"]:
        uri = platform["uri"]
        expected = platform["sha256"]
        print(f"  {uri}")
        try:
            with urllib.request.urlopen(uri) as resp:
                data = resp.read()
        except urllib.error.HTTPError as exc:
            print(f"    ERROR: returned HTTP {exc.code}", file=sys.stderr)
            ok = False
            continue
        except urllib.error.URLError as exc:
            print(f"    ERROR: unreachable: {exc.reason}", file=sys.stderr)
            ok = False
            continue
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            print(
                f"    ERROR: sha256 mismatch\n"
                f"      expected {expected}\n"
                f"      actual   {actual}",
                file=sys.stderr,
            )
            ok = False
        else:
            print(f"    OK {actual}")
    return ok


def main() -> None:
    paths = sys.argv[1:] or [
        os.path.join(PLUGINS_DIR, f)
        for f in sorted(os.listdir(PLUGINS_DIR))
        if f.endswith(".yaml")
    ]
    with open(SCHEMA_PATH) as fh:
        validator = Draft7Validator(json.load(fh), format_checker=FormatChecker())

    failed = [p for p in paths if not verify(p, validator)]
    if failed:
        rel = ", ".join(os.path.relpath(p, REPO_ROOT) for p in failed)
        print(f"\nFAILED {len(failed)} manifest(s): {rel}", file=sys.stderr)
        sys.exit(1)
    print(f"\nAll {len(paths)} manifest(s) valid and verified.")


if __name__ == "__main__":
    main()
