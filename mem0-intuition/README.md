# Mem0 intuition

[Read the rendered write-up](https://anton-dergunov.github.io/ml-explorations/mem0-intuition/mem0-intuition.html)
· [notebook](mem0-intuition.ipynb)

The vendor demo for a memory layer is `add("I like pizza")` then
`search("food")`, which shows the API and none of the mechanism. This notebook
runs the thing memory is actually for: a user talks to an assistant across three
separate sessions, changes their mind in between, and the third session has to
answer correctly with no transcript in front of it.

Every LLM and embedding call Mem0 makes is intercepted and printed, so the
extraction prompts, the consolidation behaviour and the retrieval ranking are all
visible rather than inferred.

## Running it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e .
.venv/bin/python -m ipykernel install --user --name mem0-intuition --display-name mem0-intuition
```

Put a `GEMINI_API_KEY` in a `.env` at the repository root, open the notebook in
VS Code and pick the **mem0-intuition** kernel. A full run is a handful of
`gemini-3.1-flash-lite` calls.

The vector store is a local Qdrant file under `.mem0-run/`, wiped at the top of
every run so the notebook starts clean each time.
