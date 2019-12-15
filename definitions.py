from pathlib import Path

ROOT_DIR: Path = Path(__file__).parent
LOG_DIR = ROOT_DIR / "logs"
CONFIG_DIR = ROOT_DIR / "config"
TEXT_DIR = ROOT_DIR / "text"

if not LOG_DIR.is_dir():
    LOG_DIR.mkdir()
