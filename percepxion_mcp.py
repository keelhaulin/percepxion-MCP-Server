from __future__ import annotations

import sys
from pathlib import Path

# Allow running without installing the package
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / "src"))

from percepxion_mcp.server import main  # noqa: E402


if __name__ == "__main__":
    main()
