# Union Pacific HO Scale Layout Project

![Technical wire diagram of Union Pacific Challenger 3826](resources/photos/UP3826_Challenger_sketch.png)

This repository is the authoritative digital representation of a physical
Union Pacific HO-scale model railroad. It holds the engineering documentation,
configuration, inventory, operational data, and software used to build and
operate the layout. The physical railroad is the deployed system; this
repository is its source of truth.

The project is under active development alongside construction of the physical
layout.

## Project areas

- `config/` — application configuration, including asset-data locations and ID
  prefixes.
- `data/` — persisted JSON records for rolling stock and future layout assets.
- `docs/` — engineering designs, architectural decisions, DCC material, and
  the roadmap.
- `inventory/` — physical inventory and procurement information, organized by
  asset class.
- `operations/` — operating, deployment, and maintenance procedures, such as
  JMRI material.
- `resources/` — drawings, photographs, and external reference material.
- `src/` — software source: Python railroad domain, operations, and service
  code; ESP32 firmware; and single-board-computer integrations.
- `tmp/` — local scratch space; not an authoritative project artifact.

## Software

The Python application uses a framework-independent domain and operation layer
for locomotives, cars, and maintenance-of-way equipment. JSON persistence is
handled through DAO classes; the Flask service is an optional adapter over the
operation API.

Run the test suite from the repository root:

```bash
PYTHONPATH=src python3 -m pytest
```

Run the operational command-line interface:

```bash
PYTHONPATH=src python3 -m railroad.operation.cli --help
```

Run the local web service:

```bash
python3 -m pip install "Flask>=3.0,<4.0"
PYTHONPATH=src python3 -m railroad.service --config config/railroad-conf.json
```

Or manage both local services with the repository scripts:

```bash
./app_service start     # roster UI on port 5201
./dcc_service start     # EX-CSB1 UI and serial service on port 5202
./slm_service start     # Ollama with Llama 3.2 1B on port 11434
./chat_service start    # conversational asset UI on port 5203
./app_service status
./dcc_service status
./slm_service status
./chat_service status
```

Open `http://127.0.0.1:5201/` on the host or
`http://<mac-lan-ip>:5201/` from an iPhone on the trusted layout network to
view the movable-vehicle roster. See the
[web-service design](docs/designs/090-web-service.md) for the web and JSON API
boundary, and [ADR-007](docs/decisions/ADR-007-OperatingFunctions.md) for the
operation API.

Open `http://127.0.0.1:5203/` for the separate asset-management chat interface.
It uses the same domain, DAO, and roster search behavior as `app_service`; a
search runs when Enter is pressed. Set `CHAT_SLM_URL` and `CHAT_SLM_MODEL` to
use an optional local OpenAI-compatible SLM endpoint. Without one, the service
uses its deterministic interpreter.

To use Llama 3.2 1B locally with Ollama on macOS:

```bash
brew install ollama
ollama pull llama3.2:1b
./slm_service start
./chat_service restart
curl http://127.0.0.1:5203/health
```

The health response reports `"interpreter":"slm"` when the SLM configuration
is active. Ollama runs inference locally; no Python virtual environment,
separate model SDK, or login service is required. Manage it explicitly with
`./slm_service {start|stop|restart|status}`. Start `slm_service` before
`chat_service`; if Ollama is unavailable, `chat_service` starts in rules mode.
To show the interpreted intent, raw SLM response, and fallback reason below
each chat result while diagnosing model behavior, start with
`CHAT_SLM_DEBUG=1 ./chat_service restart`.

## Planning and design

The [roadmap](docs/designs/080-roadmap.md) describes the intended destination
of the project. Architectural choices are recorded in
[docs/decisions](docs/decisions/), while system and layout designs live in
[docs/designs](docs/designs/).

---

`(Ɔ) Copyleft 2026, Snehasis Sinha`
