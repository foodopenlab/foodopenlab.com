import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_backend_dir = _here.parent.parent.parent  # com.auditor/
_apps_dir = _backend_dir / "apps"
_core_dir = _backend_dir / "core"

for _path in (_core_dir, _apps_dir):
    if _path.is_dir() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
