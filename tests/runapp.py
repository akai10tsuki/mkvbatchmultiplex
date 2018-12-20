"""Test application mkvbatchmultiplex"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mkvbatchmultiplex import mainApp # pylint: disable=C0413

def main():
    """Entry point for mkvbatchmultiplex"""

    mainApp()

if __name__ == "__main__":
    sys.exit(main())
