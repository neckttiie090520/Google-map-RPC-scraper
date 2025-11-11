# Repository Guidelines

## Project Structure & Module Organization
- Core scraping lives in `src/scraper/production_scraper.py`, RPC helpers in `src/search/`, and shared utilities (anti-bot, translation, exporters) in `src/utils/`.
- The Flask UI plus templates/static assets are in `webapp/`; demos or notebooks belong in `examples/`, and user docs stay in `docs/`.
- Tests are root-level `test_*.py` suites—extend the existing naming pattern (`test_language_*`, `test_ui_*`) so `pytest` discovers new coverage without extra wiring; large run artifacts stay in `outputs/`.

- `python -m venv .venv && .venv\Scripts\activate` (or `source .venv/bin/activate`) – standard virtual environment.
- `pip install -r requirements.txt` – installs scraper + web UI dependencies.
- `python test_scraper.py` – single-place regression hitting the production pipeline.
- `pytest -q` – runs every `test_*.py`, including translation, enforcement, and UI API checks.
- `python webapp/app.py` – serves the dashboard at `http://localhost:5000`.

## Coding Style & Naming Conventions
- Follow PEP 8 with four-space indents, <=100-character lines, grouped imports, and docstrings as outlined in `CONTRIBUTING.md`.
- Keep functions/variables in `snake_case`, classes in `PascalCase`, constants upper snake, and add type hints + docstrings for all public APIs.
- Maintain Unicode support: keep the UTF‑8 console shim and never drop helpers like `src/utils/unicode_display.py`; complex utilities should ship with a sibling `.md` explainer.

## Testing Guidelines
- Mirror existing suites when adding coverage (`test_language_consistency.py`, `test_ui_search_api.py`, etc.) so reviewers can infer scope from filenames.
- Before each PR run `python test_scraper.py`, `pytest -k <area>`, and, for UI work, a manual scrape via the Flask app in Thai and English.
- Export-facing changes need a fresh sample in `outputs/` (or redacted snippets in the PR description) so reviewers can verify schema shifts.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`feat:`, `docs:`, `chore:`) as demonstrated by `git log`; keep scopes tight and imperative.
- PRs should rebase on `main`, reference the driving issue (`Fixes #123`), include test/QA notes, and attach screenshots or JSON diffs for UI or data changes.
- Update README/CLAUDE when behaviour changes and leave secrets in local `.env` files (extend `.env.example` instead).

## Security & Configuration Tips
- Never check in `.env`; copy from `.env.example`, document new toggles inline, and store proxy or throttle credentials locally.
- Output samples can expose client data—sanitize files before sharing and prefer synthetic or truncated examples inside `examples/`.
