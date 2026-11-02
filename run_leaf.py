#!/usr/bin/env python
"""LEAF Benchmark CLI Launcher."""

import sys
from pathlib import Path

# Ensure source/ is on sys.path
root_dir = Path(__file__).resolve().parent
source_dir = root_dir / "source"
if str(source_dir) not in sys.path:
    sys.path.insert(0, str(source_dir))

from leaf.cli.main import main

if __name__ == "__main__":
    sys.exit(main())

