# EX-CSB1 web controller

The Mac is the development and lab host. The same application will later run on
the Cubietruck and Axon SBCs.

## Backend

```bash
cd src/csb1
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
CSB1_PROFILE=mac python -m backend
```

The DCC API listens on `http://0.0.0.0:5202` by default. The serial port is not
opened automatically in the Mac profile; connect it through the API after the
service starts.

From the repository root, the normal Mac workflow is:

```bash
./dcc_service start
./dcc_service status
./dcc_service restart
./dcc_service stop
```

Runtime output is written to `tmp/dcc_service.log`; the managed process ID is
stored in `tmp/dcc_service.pid`.

## Frontend

```bash
cd src/csb1/frontend
npm install
npm run dev
```

Vite listens on port 5173 and proxies API and Socket.IO traffic to port 5202.

## Tests

```bash
cd src/csb1
pytest
```
