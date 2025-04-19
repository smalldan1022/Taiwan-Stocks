import os

import yaml


class Config:
    """
    Loads configuration from YAML file or environment variables.
    """

    def __init__(self, path: str = None):
        cfg = {}
        if path and os.path.exists(path):
            with open(path) as f:
                cfg = yaml.safe_load(f)

        # database settings
        self.db = {
            "host": os.getenv("DB_HOST", cfg.get("db", {}).get("host", "localhost")),
            "port": int(os.getenv("DB_PORT", cfg.get("db", {}).get("port", 3306))),
            "user": os.getenv("DB_USER", cfg.get("db", {}).get("user", "root")),
            "password": os.getenv("DB_PASS", cfg.get("db", {}).get("password", "")),
            "db": os.getenv("DB_NAME", cfg.get("db", {}).get("db", "stocks")),
            "charset": cfg.get("db", {}).get("charset", "utf8mb4"),
        }

        # crawler settings
        self.symbols = cfg.get("symbols", ["2330", "2317"])
        # seconds between requests
        self.rate_limit = cfg.get("rate_limit", 1)
