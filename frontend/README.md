# CAreview frontend

React + TypeScript dashboard, built with Vite. This is a documented exception
to the rest of CAreview's stdlib-only/no-build-step constraint — see
[`project/decisions/DECISION-024-react-frontend-build-step.md`](../project/decisions/DECISION-024-react-frontend-build-step.md).

## Install

```sh
npm install
```

## Build (required before running the server)

```sh
npm run build
```

This compiles `src/` into `../web/index.html`, `../web/index.js`, and
`../web/index.css` — fixed, non-hashed filenames, because `server.py` serves
static files from an explicit allowlist (`STATIC_FILES` in `server.py`), not
a wildcard directory listing. `../web/sample-data.json` is untouched by the
build (`emptyOutDir: false`).

After building, run the server as usual from the repository root:

```sh
python3 server.py
```

then open <http://127.0.0.1:8765/>.

## Development

```sh
npm run dev
```

Starts Vite's dev server (typically `http://localhost:5173`) for fast
iteration on components. **This is not how the app is verified** — the dev
server has its own CSP/host behavior that has nothing to do with `server.py`'s
security posture. Always verify a change via `npm run build` +
`python3 server.py`, not the dev server.

## Tests

```sh
npm test
```

Runs the Vitest suite: severity/score logic, the typed API client's error
branches (401/403/502/network failure), the SVG gauge component, a hostile-
markup rendering check (shares the fixture with
[`tests/test_ui_safety.py`](../tests/test_ui_safety.py)'s Python-side check),
app-only secret-handling behavior, and a scan for dangerous DOM/code sinks
across `src/`.

## Structure

- `src/api/` — typed fetch client and types matching the exact backend
  contract (see the root README's [HTTP API](../README.md#http-api) section).
- `src/state/` — app-wide auth/data state (`appState.tsx`) and hash-based
  navigation (`navigation.ts`, since `server.py` has no SPA-fallback routing).
- `src/components/` — shared layout, hand-rolled SVG charts, badges.
- `src/pages/` — one file per dashboard section.
- `src/lib/` — severity/score design language and client-derived insight
  calculations (Insights page; no new backend endpoints).
- `src/test/` — Vitest + React Testing Library.
