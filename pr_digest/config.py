"""Load and validate pr_digest configuration.

Delegates the generic YAML+env work to common.config.load_yaml, then layers
the pr_digest schema on top: squad -> team_members union, required keys,
threshold defaults.
"""
from pathlib import Path

from common.config import load_yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_config(path: Path | None = None) -> dict:
    """Load pr_digest's config.yml and apply the pr-specific schema."""
    if path is None:
        path = REPO_ROOT / "config.yml"
    cfg = load_yaml(path)

    # Squads (preferred): dict of squad_name -> [handles]. We derive a flat
    # team_members union for the GitHub search query, and keep `squads` for
    # grouping the digest. Legacy flat `team_members` is treated as one squad.
    if cfg.get("squads"):
        members: list[str] = []
        for handles in cfg["squads"].values():
            members.extend(handles or [])
        cfg["team_members"] = members
    elif cfg.get("team_members"):
        cfg["squads"] = {"team": list(cfg["team_members"])}

    # minimal validation — fail loudly at startup, not mid-run
    for key in ("repos", "thresholds"):
        if key not in cfg:
            raise ValueError(f"config.yml missing required key: {key}")
    if not cfg["repos"]:
        raise ValueError("config.yml: repos list is empty")
    if not cfg.get("team_members"):
        raise ValueError("config.yml: define `squads` (or a flat `team_members` list)")

    cfg.setdefault("approvers", [])
    cfg.setdefault("exclude_paths", [])
    cfg["thresholds"].setdefault("fast_lane_max_size", 500)
    cfg["thresholds"].setdefault("fast_lane_max_files", 5)
    cfg["thresholds"].setdefault("stale_days", 7)
    cfg["thresholds"].setdefault("community_idle_cap_days", 90)

    return cfg
