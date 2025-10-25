import yaml
from pathlib import Path

def load_yaml(file_path: Path):
    """Load a YAML file and return a dictionary. Returns {} if empty or invalid."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        if data is None:
            return {}
        return data