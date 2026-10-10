"""
conftest.py - Pytest configuration adding src, scripts, and root directory to python path.
"""

import sys
from pathlib import Path

# Add src, scripts, and project root to Python sys.path
root_dir = Path(__file__).parent.parent
src_dir = root_dir / "src"
scripts_dir = root_dir / "scripts"

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(root_dir))
