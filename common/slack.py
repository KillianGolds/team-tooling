"""Slack webhook transport. Formatting stays per-tool; this just posts."""
import requests


def post_to_slack(webhook_url: str, blocks: list[dict],
                  fallback: str = "team-tooling update") -> None:
    payload = {"text": fallback, "blocks": blocks}
    r = requests.post(webhook_url, json=payload, timeout=15)
    r.raise_for_status()
