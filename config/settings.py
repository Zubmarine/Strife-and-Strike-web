import yaml
from pathlib import Path

class Settings:
    def __init__(self):
        self.config_path = Path("config/config.yaml")
        self.config = self._load_config()
        
    def _load_config(self):
        if not self.config_path.exists():
            return {}
        with open(self.config_path) as f:
            return yaml.safe_load(f)