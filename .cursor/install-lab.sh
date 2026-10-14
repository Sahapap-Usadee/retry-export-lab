#!/bin/sh
set -eu
python3 --version
git --version
python3 -c 'import sys; assert sys.version_info >= (3, 9), sys.version'
python3 -c 'import argparse, csv, pathlib, tempfile, unittest; print("lab stdlib ready")'
