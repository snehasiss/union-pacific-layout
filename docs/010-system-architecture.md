# ADR: 010 System Architecture

**Status:** Accepted  
**Date:** 10 August 2026  
**Project:** Union Pacific HO Scale Railroad

---

## Context

The railroad repository is intended to be the digital footprint of the physical Union Pacific HO scale model railroad. It should eventually contain enough information and software to allow another person to reproduce all or part of the railroad.

The initial locomotive data was imported from CSV files and converted into JSON records. CSV was useful as an initial data-entry/import mechanism, but it is not expected to be part of the normal lifecycle of the railroad data.

The design has also evolved from a simple `steam/` and `diesel/` hierarchy toward a generic domain model in which a `Locomotive` contains common attributes and a type-specific `Engine` component.

The repository must also support other physical railroad entities such as:

- Locomotives
- Freight and passenger cars
- Signals
- Turnouts or Switches
- MOW (Maintenance of Way) and other motorized machines

Each physical item requires a persistent unique identifier.

---

## Decisions

### 1. JSON is the canonical persistent representation

After initial CSV import, the normal lifecycle is:

```text
JSON <-> ⟷ Domain Object <-> JSON
A ↔ B ⇌ C ⇔ D ⇄ E
```

CSV-to-JSON conversion is considered a one-time import/migration utility rather than a core application function.

The canonical railroad data will therefore be maintained as JSON records.

---

### 2. `config/` contains configuration only

CSV files are not configuration files and will not be stored under `config/`.

The `config/` directory is reserved for actual application, roster, or system configuration, for example:

```text
config/
├── application.json
└── ...
```

Configuration should preferably use portable paths rather than machine-specific absolute filesystem paths.

---

### 3. CSV import is an independent tool

The existing CSV files and their importer will be moved under a dedicated tool area:

```text
src/
└── tools/
    └── loco_import/
        ├── loco_import.py
        ├── steam.csv
        └── diesel.csv
```

The importer performs:

```text
CSV
 ↓
normalized record
 ↓
DataclassFactory
 ↓
Domain Object
 ↓
IOStream.create()
 ↓
JSON
```

Once the initial import is complete, the CSV files and importer are no longer part of the normal operational lifecycle.

---

### 4. Persistent data is stored under `data/`

JSON files are data, not configuration.

The repository will use a single data directory rather than separate directories for each entity type:

```text
data/
├── L000001.json
├── L000002.json
├── C000001.json
├── G000001.json
├── W000001.json
└── M000001.json
```

The unique identifier and its prefix provide the primary namespace/type distinction.

The exact prefix taxonomy will be finalized as additional domain entities are implemented.

---

### 5. Every physical item has a permanent unique identifier

Prototype identity and physical model identity are different concepts.

For example, two physical models may both represent:

```text
Union Pacific 4014
```

but they must have different internal IDs:

```text
L000001
L000002
```

The identifier is the equivalent of a primary key in a relational database.

It is:

- Unique
- Persistent
- Immutable
- Independent of railroad reporting mark
- Independent of road number
- Independent of DCC address

The JSON filename is derived from this identifier:

```text
L000001.json
```

rather than from the prototype road number:

```text
UP4014.json
```

This avoids collisions when multiple physical models represent the same prototype.

---

### 6. Road number is not a unique primary key

`reporting_mark + road_number` represents prototype identity and is therefore not guaranteed to be unique within the model railroad collection.

The following are valid:

```text
L000001 → UP 4014
L000002 → UP 4014
```

A roster may therefore contain multiple physical models representing the same prototype.

The `Roster` will provide secondary lookup operations such as:

```python
find_by_id("L000001")
find_by_road_number("UP", 4014)
find_by_dcc_address(4014)
find_by_status("active")
find_by_type("steam")
```

`find_by_id()` returns a single object.

Other searches may return multiple objects.

---

### 7. DCC address is an operational identity

DCC address is separate from prototype identity.

The convention is to use the road number as the DCC address where practical, but this is not a mandatory identity rule.

The actual operational constraint is:

> An active DCC-controlled locomotive must not share a DCC address with another active DCC-controlled locomotive.

For example:

```text
L000001
Prototype: UP 4014
DCC address: 4014

L000002
Prototype: UP 4014
DCC address: 9401
```

Both remain valid representations of the same prototype.

The `Roster` or relevant domain service will eventually enforce DCC-address uniqueness for active units.

---

### 8. Locomotive uses composition rather than separate top-level Steam/Diesel classes

The common domain object is:

```python
@dataclass
class Locomotive:
    id: str
    type: str
    prototype: Prototype
    model: Model
    control: Control
    ownership: Ownership
    media: Media
    engine: Engine
    status: LocoStatus
```

The type-specific characteristics are represented through the `Engine` component:

```text
Locomotive
├── common attributes
└── engine
    ├── Steam
    ├── Diesel
    └── MOW
```

This avoids creating separate `SteamLoco`, `DieselLoco`, and `MOWLoco` top-level domain classes unless future requirements demonstrate that inheritance is necessary.

The exact terminology of `Engine` may be revisited later if a more meaningful domain term emerges.

---

### 9. Locomotive operational status is explicitly modeled

The current lifecycle states are:

```python
class LocoStatus(Enum):
    ACTIVE = "active"
    REPAIR = "repair"
    BOXED = "boxed"
    RETIRED = "retired"
```

Definitions:

| Status | Meaning |
|---|---|
| `active` | Available and operational on the layout |
| `repair` | Present but undergoing maintenance or repair |
| `boxed` | Owned and stored, not currently deployed |
| `retired` | Permanently withdrawn from operational use but retained as part of the railroad's historical record |

`retired` is intentionally preferred over `removed`, `deleted`, or `sold`.

The JSON record should not normally be physically deleted merely because a locomotive is retired.

If a locomotive is eventually dismantled or otherwise removed from active ownership, the historical record remains available.

If necessary in the future, a retired locomotive can use a neutral reporting mark such as `XX` to avoid conflicting with a later active model carrying the same railroad number. This is a domain operation and should not be performed automatically by the persistence layer.

---

### 10. IOStream becomes the persistence/DAO layer

`IOStream` is no longer primarily a CSV/JSON conversion utility.

Its principal responsibility is persistent JSON data access:

```python
class IOStream:

    def create(self, obj):
        ...

    def get(self, object_id):
        ...

    def find(self, **criteria):
        ...

    def update(self, obj):
        ...

    def retire(self, object_id):
        ...
```

Potential future operation:

```python
purge(object_id)
```

would represent physical deletion and should be exceptional.

The application/domain layer should not directly call `json.dump()`, `json.load()`, or manipulate JSON filenames.

---

### 11. `get()` and `find()` have different semantics

`get()` is a primary-key lookup:

```python
loco = io.get("L000001")
```

It is expected to return one object.

`find()` is a query operation:

```python
locos = io.find(
    reporting_mark="UP",
    road_number=4014
)
```

It may return multiple objects.

This distinction allows the system to maintain a relational-database-like primary key while still supporting convenient railroad-oriented searches.

---

### 12. `create()`, `update()`, and `retire()` operate on domain objects

The application should work with domain objects rather than JSON dictionaries.

Example:

```python
loco = io.get("L000001")

loco.status = LocoStatus.REPAIR

io.update(loco)
```

The IO layer is responsible for serializing the object back to JSON.

Similarly:

```python
io.create(loco)
```

creates the persistent record.

And:

```python
io.retire("L000001")
```

changes the domain status to `RETIRED` and persists the change without deleting the record.

---

### 13. DataclassFactory remains a generic object-construction utility

The `DataclassFactory` was initially developed primarily to support CSV import.

Its long-term role should be narrowed and clarified:

> Construct domain dataclass objects from structured records.

It may continue to be used by `IOStream` when reconstructing nested domain objects from JSON, particularly because the domain model contains nested dataclasses:

```text
Locomotive
├── Prototype
├── Model
├── Control
├── Ownership
├── Media
└── Engine
    └── Steam / Diesel / MOW
```

However, `DataclassFactory` is not responsible for persistence and should not contain JSON file management logic.

---

## Resulting Repository Structure

The current target structure is:

```text
union-pacific-layout/
│
├── config/
│   ├── application.json
│   └── ...
│
├── data/
│   ├── L000001.json
│   ├── L000002.json
│   ├── C000001.json
│   ├── G000001.json
│   ├── W000001.json
│   └── M000001.json
│
├── src/
│   ├── scripts/
│   │   ├── libs/
│   │   │   ├── locomotive.py
│   │   │   ├── roster.py
│   │   │   ├── dataclassfactory.py
│   │   │   └── iostream.py
│   │   └── locobuild.py
│   │
│   └── tools/
│       └── loco_import/
│           ├── loco_import.py
│           ├── steam.csv
│           └── diesel.csv
│
├── operations/
├── resources/
├── trains/
└── README.md
```

`src/scripts/utils/libs/` is simplified to `src/scripts/libs/`.

The exact Python package structure may be refactored later if the software grows into a conventional Python package.

---

## Architectural Principle

The repository now has a clear separation of concerns:

```text
config/      → How the software behaves
data/        → What the railroad currently is
src/         → Software that operates on the data
tools/       → One-time/import/maintenance utilities
operations/  → How the railroad is operated
resources/   → Supporting artifacts
trains/      → Prototype and model railroad documentation
```

The central runtime model is:

```text
                  DOMAIN OBJECTS
                       │
              ┌────────┼────────┐
              │        │        │
         Locomotive    Car    Signal ...
              │
              ▼
            Roster
              │
              ▼
          IOStream / DAO
              │
              ▼
             JSON
              │
              ▼
             data/
```

This architecture intentionally treats the JSON files as the **persistent digital representation of the physical railroad**, while keeping configuration, source code, import tools, and documentation separate.
