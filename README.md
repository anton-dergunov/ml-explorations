# ML Explorations

Small, self-contained experiments — each one a single notebook that takes a
question about some ML system, runs it, and writes up what came back. The
executed outputs are committed along with the code, so every result can be read
without running anything.

Each experiment is rendered to a page at
**[anton-dergunov.github.io/ml-explorations](https://anton-dergunov.github.io/ml-explorations/)**.
GitHub's own notebook view works well on a desktop but often gives up on a
tablet or phone, so the rendered page is the better link to follow and to share.

## Experiments

| Experiment | What it looks at | |
|---|---|---|
| **Mem0 intuition** | What an LLM memory layer really stores, what happens when a user changes their mind, and whether retrieval can tell the current fact from the stale one | [read](https://anton-dergunov.github.io/ml-explorations/mem0-intuition/mem0-intuition.html) · [notebook](mem0-intuition/mem0-intuition.ipynb) |

## Running one yourself

Every experiment directory is independent and carries its own `pyproject.toml`
and README. In general:

```bash
cd <experiment>
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e .
.venv/bin/python -m ipykernel install --user --name <experiment> --display-name <experiment>
```

Then open the notebook in VS Code and select that kernel. Anything needing an
API key reads it from a `.env` at the repository root; the experiment's README
says which keys it wants.

## How the notebooks are stored

The `.ipynb` is the version in git, outputs included, because the outputs are
the point — the prose, the code and the results together are what makes the
notebook worth reading.

Each notebook is also paired by [jupytext](https://jupytext.readthedocs.io/)
with a percent-format script, `<name>.nb.py`: the same content as plain Python,
which is far easier to diff, to search, and to hand to a coding assistant when necessary. That
file is generated and gitignored — the `.nb.py` suffix exists so a single
`.gitignore` line can skip it while ordinary Python files stay tracked. The
pairing lives in the notebook's metadata, so any clone can recreate it:

```bash
jupytext --sync path/to/notebook.ipynb
```

VS Code users get both directions as tasks (`.vscode/tasks.json`), each guarded
so that a sync fails loudly rather than quietly overwriting the side that has
newer work in it.

Two notes if you work this way. `git diff` on a notebook is JSON noise by
default, which a one-time textconv driver fixes:

```bash
git config diff.ipynb.textconv 'jupytext --to py:percent --output -'
printf '*.ipynb diff=ipynb\n' >> .gitattributes
```

And when a script is synced back into a notebook, jupytext keeps the outputs
already there — including on cells whose code changed. Re-run those cells before
committing, or the notebook will show results its code never produced.

## Publishing

Every push to `main` renders the notebooks with `nbconvert` and deploys them to
GitHub Pages. Nothing is executed during the build; the committed outputs are
what gets published. To preview locally:

```bash
python tools/build_site.py && open _site/index.html
```
