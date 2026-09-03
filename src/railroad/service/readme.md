## Railroad web service

This package is the Flask/web adapter over `railroad.operation`. It does not
own lifecycle, roster, or persistence rules.

Run the development server from the repository root:

```bash
python3 -m pip install "Flask>=3.0,<4.0"
PYTHONPATH=src python3 -m railroad.service --config config/railroad-conf.json
```

Open `http://127.0.0.1:5000/` for the roster UI. It is a responsive
client-side workspace that fetches its data from this service's JSON boundary;
Locomotives, Cars, and MOW equipment share the same navigation and detail
views.

## Routes

- `GET /` — roster application shell.
- `GET /assets/<id>` — asset-detail application shell, including retired
  records.
- `GET /api/assets` — active roster JSON. Optional query parameters are
  `type=all|loco|car|mow`, `reporting_mark`, `status`, and `q` for the core
  case-insensitive free-text roster search.
- `GET /api/assets/<id>` — JSON for an individual asset, including retired
  records.
- `GET /api/assets/<id>/media` — attributed, curated representative-media
  metadata for an asset. The browser loads image thumbnails only when Media is
  selected.
- `POST /assets` — create a default Loco, Car, or MOW and apply a JSON patch.
- `POST /assets/<id>/update` — apply a JSON patch and persist it.
- `POST /assets/<id>/retire` — retire an asset.

The routes delegate to the framework-independent operation layer. Templates,
styles, browser code, and curated presentation-media metadata stay in this
package under `templates/`, `static/`, and `media.py`.
