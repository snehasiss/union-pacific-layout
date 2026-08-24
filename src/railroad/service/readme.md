## Railroad web service

This package is the Flask/web adapter over `railroad.operation`. It does not
own lifecycle, roster, or persistence rules.

Run the development server from the repository root:

```bash
python3 -m pip install "Flask>=3.0,<4.0"
PYTHONPATH=src python3 -m railroad.service --config config/railroad-conf.json
```

Open `http://127.0.0.1:5000/` for the roster UI. The adapter provides roster
search and asset detail pages plus JSON endpoints for asset creation, update,
and retirement.
