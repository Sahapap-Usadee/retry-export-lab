#!/bin/sh
set -eu
python3 --version
git --version
python3 -c 'import sys; assert sys.version_info >= (3, 9), sys.version'
python3 -c 'import argparse, csv, pathlib, tempfile, unittest; print("lab stdlib ready")'

# Repo file is the source of truth. pstack skills read the home path.
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
mkdir -p "$HOME/.cursor/rules" && cp "$repo_root/.cursor/rules/pstack-models.mdc" "$HOME/.cursor/rules/pstack-models.mdc"
