import runpy
from pathlib import Path


def test_device_scripts_run_without_script_path_errors():
    root = Path(__file__).resolve().parent
    runpy.run_path(str(root / "deck_pull.py"))
    runpy.run_path(str(root / "deck_upload.py"))
