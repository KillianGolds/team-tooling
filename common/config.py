"""Generic YAML config loader, tool-agnostic.

Each tool's config module is expected to wrap `load_yaml` with its own
schema checks and defaults. This module knows nothing about squads,
thresholds, or any pr_digest specifics — it just locates a YAML file,
parses it, and interpolates env references like ${GH_TOKEN} or $VAR in
any string value.
"""
import os
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict:
    """Load a YAML file and expand $VAR / ${VAR} env references in any
    string value (recursive: dicts and lists are walked).

    Returns a plain dict (empty if the file was empty). Raises whatever
    yaml/open raise; deliberately no validation here — that's per-tool.
    """
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    return _expand_env(cfg)


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value
