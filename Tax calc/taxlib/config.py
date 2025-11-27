import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'taxflow_config.json')

def _load():
    try:
        with open(_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save(cfg):
    try:
        with open(_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def get(key, default=None):
    cfg = _load()
    return cfg.get(key, default)

def set(key, value):
    cfg = _load()
    cfg[key] = value
    _save(cfg)
"""Simple configuration persistence for the TaxFlow application.

Stores small user preferences like theme and language in JSON file.
"""
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'taxflow_config.json')


def _load():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save(cfg: dict):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def get(key, default=None):
    cfg = _load()
    return cfg.get(key, default)


def set(key, value):
    cfg = _load()
    cfg[key] = value
    return _save(cfg)
