#!/usr/bin/env python3
"""Render every notebook in the repository to static HTML for GitHub Pages.

Nothing is executed: the committed outputs are what gets rendered. Run it
locally the same way CI does, then open _site/index.html:

    python tools/build_site.py
"""
from __future__ import annotations

import html
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
SKIP_DIRS = {"_site", "tools", ".git", ".github", ".vscode", "node_modules"}

REPO_SLUG = os.environ.get("GITHUB_REPOSITORY", "anton-dergunov/ml-explorations")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")


@dataclass
class Notebook:
    source: Path  # relative to ROOT
    page: Path  # relative to SITE
    title: str
    summary: str

    @property
    def blob_url(self) -> str:
        return f"https://github.com/{REPO_SLUG}/blob/{BRANCH}/{self.source.as_posix()}"


def discover() -> list[Path]:
    found = []
    for path in sorted(ROOT.rglob("*.ipynb")):
        rel = path.relative_to(ROOT)
        if any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts):
            continue
        found.append(rel)
    return found


def describe(path: Path) -> tuple[str, str]:
    """Title from the first markdown heading, summary from the paragraph under it."""
    notebook = json.loads((ROOT / path).read_text())
    title, summary = path.stem, ""
    for cell in notebook["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        lines = "".join(cell["source"]).splitlines()
        heading = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
        if heading is None:
            continue
        title = lines[heading][2:].strip()
        rest = [l.strip() for l in lines[heading + 1:]]
        paragraph: list[str] = []
        for line in rest:
            if not line:
                if paragraph:
                    break
                continue
            paragraph.append(line)
        summary = " ".join(paragraph)
        break
    return title, summary


def render(path: Path) -> Path:
    out_dir = SITE / path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable, "-m", "nbconvert",
            "--to", "html",
            "--output-dir", str(out_dir),
            "--output", f"{path.stem}.html",
            str(ROOT / path),
        ],
        check=True,
    )
    return (out_dir / f"{path.stem}.html").relative_to(SITE)


INDEX_CSS = """
:root { color-scheme: light dark; --fg: #1a1a1a; --muted: #5c5c5c; --bg: #fdfdfc;
        --card: #ffffff; --line: #e4e4e0; --link: #0b5cad; }
@media (prefers-color-scheme: dark) {
  :root { --fg: #e8e8e6; --muted: #a0a09c; --bg: #16161a; --card: #1e1e23;
          --line: #32323a; --link: #7ab8f5; }
}
* { box-sizing: border-box; }
body { margin: 0; padding: 3rem 1.5rem 5rem; background: var(--bg); color: var(--fg);
       font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
main { max-width: 46rem; margin: 0 auto; }
h1 { font-size: 1.9rem; margin: 0 0 .4rem; letter-spacing: -.01em; }
.lede { color: var(--muted); margin: 0 0 2.5rem; }
article { border: 1px solid var(--line); background: var(--card); border-radius: 10px;
          padding: 1.15rem 1.35rem; margin-bottom: 1rem; }
article h2 { font-size: 1.12rem; margin: 0 0 .35rem; }
article h2 a { color: var(--fg); text-decoration: none; }
article h2 a:hover { color: var(--link); }
article p { margin: 0 0 .8rem; color: var(--muted); font-size: .94rem; }
.links { display: flex; flex-wrap: wrap; gap: .5rem; }
.links a { font-size: .82rem; text-decoration: none; color: var(--link);
           border: 1px solid var(--line); border-radius: 999px; padding: .22rem .7rem; }
.links a:hover { border-color: var(--link); }
footer { margin-top: 3rem; color: var(--muted); font-size: .84rem; }
footer a { color: var(--link); }
"""


def write_index(notebooks: list[Notebook]) -> None:
    cards = []
    for nb in notebooks:
        summary = f"<p>{html.escape(nb.summary)}</p>" if nb.summary else ""
        cards.append(
            f'<article>\n'
            f'  <h2><a href="{nb.page.as_posix()}">{html.escape(nb.title)}</a></h2>\n'
            f'  {summary}\n'
            f'  <div class="links">\n'
            f'    <a href="{nb.page.as_posix()}">Read the write-up</a>\n'
            f'    <a href="{nb.blob_url}">Notebook on GitHub</a>\n'
            f'  </div>\n'
            f'</article>'
        )
    (SITE / "index.html").write_text(
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>ML Explorations</title>\n"
        f"<style>{INDEX_CSS}</style>\n"
        "</head><body><main>\n"
        "<h1>ML Explorations</h1>\n"
        '<p class="lede">Small self-contained experiments, each one written up as a '
        "notebook and rendered here with the outputs it actually produced.</p>\n"
        + "\n".join(cards)
        + f'\n<footer>Source: <a href="https://github.com/{REPO_SLUG}">'
          f"github.com/{REPO_SLUG}</a></footer>\n"
        "</main></body></html>\n"
    )


def main() -> int:
    paths = discover()
    if not paths:
        print("no notebooks found", file=sys.stderr)
        return 1

    shutil.rmtree(SITE, ignore_errors=True)
    SITE.mkdir(parents=True)
    (SITE / ".nojekyll").touch()  # keep Pages from running the content through Jekyll

    notebooks = []
    for path in paths:
        title, summary = describe(path)
        page = render(path)
        notebooks.append(Notebook(source=path, page=page, title=title, summary=summary))
        print(f"  {path}  ->  _site/{page}   ({title})")

    write_index(notebooks)
    print(f"\n{len(notebooks)} notebook(s) rendered into {SITE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
