"""Write the reports/ evidence pages. Fully derived state: the directory
is wiped and regenerated every run, so a page that disappears from a git
diff means that test aged out of the window or stopped flaking. Writing
over the old set instead would leave stale pages indistinguishable from
live ones, especially across key changes.
"""
import shutil
from pathlib import Path

from flake_digest.markdown_formatter import (
    ensure_render_safe,
    render_report_page,
    report_filename,
)


def build_pages(state: dict) -> dict[str, str]:
    """Render every record's page and run ensure_render_safe on each."""
    pages = {}
    for rec in state["flakes"].values():
        page = render_report_page(rec)
        name = report_filename(rec)
        ensure_render_safe(page, f"reports/{name}")
        pages[name] = page
    return pages


def write_reports(state: dict, out_dir: Path) -> list[str]:
    """Regenerate all pages under out_dir; returns the filenames written."""
    pages = build_pages(state)
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    for name, page in pages.items():
        (out_dir / name).write_text(page)
    return sorted(pages)
