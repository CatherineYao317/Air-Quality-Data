# Air Quality Data Analysis (Reproducible Pipeline)

This repo is configured to run a fully reproducible pipeline via **GitHub Actions + uv + Quarto**.  
Breaking the file/path contracts below will break CI and can break `main`.

## What CI Runs
The workflow lives at:
- `.github/workflows/pipeline.yml`

It performs:
1. `uv sync --frozen` (installs locked deps)
2. `uv run python analysis/00_smoke_test.py` (runs analysis)
3. `quarto render report/test_report.qmd` (renders HTML)
4. Uploads `report/test_report.html` as an artifact
5. Deploys to GitHub Pages using `site/index.html`

## Contract Files (Update Together)
These files are tightly coupled. If you rename/move one, you MUST update the workflow accordingly.

### 1) Analysis entrypoint
- Script: `analysis/00_smoke_test.py`
- Expected outputs location: `outputs/` (repo root)
- Feel free to delete/add/modify this once the actual analysis are in

If you change the script name/path or where it writes outputs:
- Update `.github/workflows/pipeline.yml` step that runs the script
- Update any paths used by the report

### 2) Quarto report + HTML output
- Input: `report/test_report.qmd`
- Output: `report/test_report.html`
- Pages entry (if enabled): `site/index.html` (copied from `report/test_report.html`)

If you rename the `.qmd` or change the HTML filename:
- Update `.github/workflows/pipeline.yml`:
    - `quarto render ...`
    - `cp report/... site/index.html`
    - artifact upload `path: report/...`

### 3) Dependencies (uv)
- `pyproject.toml` (declares deps)
- `uv.lock` (locked versions used by CI)

If you add/remove/change dependencies:
1. Run `uv sync`
2. Commit BOTH `pyproject.toml` and `uv.lock`

## Do Not Commit
Add to `.gitignore` (or keep ignored):
- `.venv/`
- `outputs/`
- `.idea/`
- `__pycache__/`

## Safe Team Workflow (Do NOT break main)
1. Work on a feature branch
2. Run locally:
    - `uv sync`
    - `uv run python analysis/00_smoke_test.py`
    - `quarto render report/test_report.qmd`
3. Ensure GitHub Actions is green
4. Only then merge to `main`

## One-line Rule
If you change ANY filename/path/output, update `.github/workflows/pipeline.yml` in the same PR.
