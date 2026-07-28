"""Load and validate flake_digest configuration.

Delegates the generic YAML+env work to common.config.load_yaml, mirroring
pr_digest's loader shape.
"""
import os
from pathlib import Path

from common.config import load_yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.yml"


def load_config(path: Path | None = None) -> dict:
    if path is None:
        env_path = os.environ.get("FLAKE_DIGEST_CONFIG")
        path = Path(env_path) if env_path else DEFAULT_CONFIG_PATH
    cfg = load_yaml(path)

    if not cfg.get("midstream"):
        raise ValueError("config.yml: define at least one `midstream` repo entry")
    for entry in cfg["midstream"]:
        for key in ("repo", "job_pattern"):
            if not entry.get(key):
                raise ValueError(f"config.yml: midstream entry missing `{key}`")
        entry.setdefault("job_level_only", [])
        entry.setdefault("bare_untrusted_until_migrated", [])

    cfg.setdefault("window_days", 30)
    cfg.setdefault("issue", {})
    cfg["issue"].setdefault("repo", None)
    cfg["issue"].setdefault("number", None)
    return cfg


def is_job_level_only(target: str, entry: dict) -> bool:
    """Targets that never get test-level parsing (structural: they emit
    no usable per-test results at all)."""
    return target in entry["job_level_only"]


def bare_untrusted(target: str, entry: dict) -> bool:
    """Targets whose bare e2e_results.json is a pre-migration clobbered
    file. Transition-era config; see the comment in config.yml."""
    return target in entry["bare_untrusted_until_migrated"]
