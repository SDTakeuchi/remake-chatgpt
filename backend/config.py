"""YAML から LLM 設定を読み込む（docs/prompts 仕様準拠）。"""
import os
from pathlib import Path

import yaml

# Docker では CONFIG_PATH=/app/config/env.yaml を指定し、config をマウントする
_default = Path(__file__).resolve().parent.parent / "config" / "env.yaml"
CONFIG_PATH = Path(os.environ.get("CONFIG_PATH") or _default)


def load_config() -> dict:
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not data or "llm" not in data:
        raise ValueError("config must have llm section")
    return data
