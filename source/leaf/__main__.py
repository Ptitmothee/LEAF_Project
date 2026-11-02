"""Direct execution entrypoint: python -m leaf."""

import sys

from leaf.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
