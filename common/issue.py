"""Rewrite-in-place mechanics for a pinned always-current issue.

What goes in the body stays per-tool; this holds the write-token
convention and the update call, shared by pr_digest and flake_digest.
"""
import os

from common.github_client import GitHubClient


def resolve_write_token(read_token: str | None = None) -> str | None:
    """Issue updates use a separately-scoped token: in CI the workflow's
    built-in GITHUB_TOKEN (issues:write on this repo only) arrives as
    ISSUE_TOKEN, while locally one PAT usually does both jobs, so this
    falls back to the read token."""
    return os.environ.get("ISSUE_TOKEN") or read_token


def rewrite_issue(repo: str, number: int, body: str, token: str) -> None:
    """Replace the body of `repo`#`number` ("owner/name" form)."""
    owner, name = repo.split("/", 1)
    GitHubClient(token).update_issue_body(owner, name, number, body)
