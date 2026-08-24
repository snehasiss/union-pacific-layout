# Railroad Web Service

## Purpose

`src/railroad/service` is the Flask adapter over `railroad.operation`. It
provides a small server-rendered web UI and JSON mutation endpoints without
moving lifecycle, roster, or persistence rules out of the operation layer.

## Structure

```text
src/railroad/service/
├── __init__.py       # create_app(config_path) factory
├── __main__.py       # development-server entry point
├── routes.py         # Flask routes and JSON boundary mapping
├── templates/
│   ├── roster.html   # movable-vehicle roster/search page
│   └── asset.html    # asset detail and retirement page
└── readme.md         # developer startup instructions
```

## UI

- `/` displays the non-retired movable roster with reporting-mark and status
  filters.
- `/assets/<id>` displays a persisted asset, including retired records, as a
  safe JSON view and offers retirement for active records.

The web UI is intentionally roster-focused. Signals, turnouts, and active
trackside equipment will appear in a future `Layout` UI rather than this
block-occupying vehicle roster.

## JSON endpoints

| Method | Route | Operation |
|---|---|---|
| `POST` | `/assets` | Create a default Loco, Car, or MOW and apply an optional JSON patch. |
| `POST` | `/assets/<id>/update` | Apply a JSON patch and persist it. |
| `POST` | `/assets/<id>/retire` | Retire the asset and redirect to its detail page. |

The routes delegate to `Asset.create`, `Asset.view`, `asset.update`,
`asset.retire`, and `Roster.from_config/search`. They do not directly write
JSON files.

## Development startup

Install runtime dependencies and start the service from the repository root:

```bash
python3 -m pip install "Flask>=3.0,<4.0"
PYTHONPATH=src python3 -m railroad.service --config config/railroad-conf.json
```

The development server binds to `127.0.0.1:5000` by default. Use `--host`,
`--port`, and `--debug` as needed.
