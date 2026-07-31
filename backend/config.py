"""YAML から LLM 設定を読み込む（docs/prompts 仕様準拠）。"""
import os
from pathlib import Path
from typing import Any, TypedDict, cast

import yaml

# Docker では CONFIG_PATH=/app/config/env.yaml を指定し、config をマウントする
_default = Path(__file__).resolve().parent.parent / "config" / "env.yaml"
CONFIG_PATH = Path(os.environ.get("CONFIG_PATH") or _default)


class LLMConfig(TypedDict, total=False):
    api_key: str
    base_url: str
    model: str


class AppConfig(TypedDict):
    llm: LLMConfig


def load_config() -> AppConfig:
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    data: Any = yaml.safe_load(raw)
    if not isinstance(data, dict) or "llm" not in data:
        raise ValueError("config must have llm section")
    return cast(AppConfig, data)
