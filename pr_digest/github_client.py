"""Thin GitHub API wrapper. Only the bits we need, with sane retry."""
import time
from fnmatch import fnmatch

import requests

API_BASE = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str):
        # Strip whitespace/newlines defensively: pasting a token into a GitHub
        # repo secret commonly picks up a trailing \n, which requests rejects
        # when building the Authorization header.
        token = (token or "").strip()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def _get(self, url: str, params: dict | None = None) -> dict | list:
        for attempt in range(3):
            r = self.session.get(url, params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (403, 429):
                # secondary rate-limit or abuse detection — back off
                reset = int(r.headers.get("X-RateLimit-Reset", 0))
                wait = max(reset - time.time(), 2 ** attempt)
                time.sleep(min(wait, 60))
                continue
            r.raise_for_status()
        r.raise_for_status()
        return {}  # unreachable, satisfies type checker

    def search_open_prs(self, repos: list[str], authors: list[str]) -> list[dict]:
        """Find open PRs by team across upstream repos.

        Filters out drafts and PRs labeled do-not-merge / hold at query time.
        """
        repo_q = " ".join(f"repo:{r}" for r in repos)
        author_q = " ".join(f"author:{a}" for a in authors)
        q = (
            f"is:pr is:open draft:false {repo_q} {author_q} "
            f"-label:do-not-merge -label:hold -label:\"do-not-merge/hold\""
        )

        items: list[dict] = []
        page = 1
        while page <= 10:  # safety cap
            data = self._get(
                f"{API_BASE}/search/issues",
                params={"q": q, "per_page": 100, "page": page},
            )
            batch = data.get("items", [])
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return items

    def get_pr_files(self, owner: str, repo: str, number: int) -> list[dict]:
        """Per-file diff stats for a PR. Paginates through all files."""
        files: list[dict] = []
        page = 1
        while page <= 30:  # PRs with >3000 files are pathological; cap.
            data = self._get(
                f"{API_BASE}/repos/{owner}/{repo}/pulls/{number}/files",
                params={"per_page": 100, "page": page},
            )
            files.extend(data)
            if len(data) < 100:
                break
            page += 1
        return files

    def get_pr_comments(self, owner: str, repo: str, number: int) -> list[dict]:
        """Issue comments on a PR — where Prow `/lgtm` style commands live."""
        comments: list[dict] = []
        page = 1
        while page <= 10:  # safety cap; >1000 comments on one PR is pathological
            data = self._get(
                f"{API_BASE}/repos/{owner}/{repo}/issues/{number}/comments",
                params={"per_page": 100, "page": page},
            )
            comments.extend(data)
            if len(data) < 100:
                break
            page += 1
        return comments

    def update_issue_body(self, owner: str, repo: str, number: int, body: str) -> None:
        """PATCH an issue's body. Used to refresh the always-current digest issue."""
        url = f"{API_BASE}/repos/{owner}/{repo}/issues/{number}"
        r = self.session.patch(url, json={"body": body}, timeout=30)
        r.raise_for_status()


def _path_excluded(filename: str, patterns: list[str]) -> bool:
    # `**/foo` is intended as "foo at any depth, including top-level",
    # but fnmatch's `**/` requires a literal `/`. Also check the basename.
    basename = filename.rsplit("/", 1)[-1]
    for pat in patterns:
        if fnmatch(filename, pat):
            return True
        if pat.startswith("**/") and fnmatch(basename, pat[3:]):
            return True
    return False


def filtered_size(files: list[dict], exclude_patterns: list[str]) -> tuple[int, int]:
    """Sum additions+deletions, ignoring files matching exclude_patterns.

    Returns (effective_line_count, effective_file_count).
    """
    total = 0
    file_count = 0
    for f in files:
        if _path_excluded(f["filename"], exclude_patterns):
            continue
        total += f.get("additions", 0) + f.get("deletions", 0)
        file_count += 1
    return total, file_count
