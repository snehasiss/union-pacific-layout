# ADR-007: Operating Functions API

- **Status:** Accepted
- **Date:** 2026-08-24
- **Related:** ADR-006 Railroad Asset Data Model and Operations

## Context

The railroad needs application operations over persisted JSON without coupling
the domain to a user interface or transport framework. Those operations must
work uniformly for movable railroad vehicles and be extensible to future
railroad assets.

The public API must be object-centric. It must not expose per-type facades such
as `LocoOps`, `CarOps`, or `MowOps`.

## Decision

`railroad.operation` is the framework-independent application layer. It owns
loading, persistence, ID/type resolution, object update, retirement, creation,
and collection search. Flask, REST, mobile, and command-line interfaces are
adapters over this API and do not contain domain or persistence rules.

### `Asset`: one persisted object

`Asset` is the generic operational wrapper for a persisted railroad object.
Create an unbound gateway with configuration, then use `view` or `create` to
obtain a bound asset.

```python
from railroad.config import Config
from railroad.operation import Asset

config = Config("config/railroad-conf.json")
assets = Asset(config)
```

#### `view(id)`

`view` resolves the entity type from its persistent ID, selects the matching
DAO, loads the JSON object, and returns a bound `Asset`.

```python
asset = assets.view("L001")
print(asset.id)
print(asset.model.status)
```

`view` includes retired records. It validates that the loaded object matches
the entity type encoded in its ID.

#### `update()`

Modify the bound domain object through the asset, then persist it with
`update()`.

```python
asset = assets.view("L001")
asset.model.note = "Decoder checked"
asset.update()
```

`update()` validates the bound object's identity and ID/type consistency before
saving. It returns the same bound `Asset` for chaining.

#### `retire()`

`retire()` changes the bound object's `model.status` to `Status.RETIRED` and
persists it.

```python
asset = assets.view("L001")
asset.retire()
```

Retirement is not deletion. The object remains accessible through `view(id)`
and is excluded only from operational collections.

#### `create(entity_type, builder, ...)`

`create` is the generic factory operation. It allocates an ID in the selected
entity namespace, builds the concrete domain object from the assigned
`Identity`, validates it, persists it, and returns a bound `Asset`.

```python
from railroad.domain.identity import EntityType

created = assets.create(
    EntityType.LOCO,
    build_loco,
    railroad="Union Pacific",
    reporting_mark="UP",
    road_number="4014",
)
```

The caller provides the concrete builder because Loco, Car, and MOW have
different type-specific fields. `Asset` owns generic identity allocation and
persistence only.

### `Roster`: movable vehicle collection

`Roster` represents movable track vehicles that can occupy track blocks:

```text
Loco, Car, MOW
```

Build one from persisted data with `from_config`, or from an existing iterable
of domain objects.

```python
from railroad.operation import Roster
from railroad.domain.model import Status

roster = Roster.from_config(config)
active_ids = roster.search({"model.status": Status.ACTIVE})
up_ids = roster.search({"reporting_mark": "UP"})
```

`search(criteria)` returns persistent IDs, not objects. Criteria are attribute
paths, so nested fields such as `model.status` are supported. `search()` with
no criteria returns every non-retired ID in roster order.

`Roster` always excludes `Status.RETIRED` objects, whether it is built from
an iterable or loaded from persistence.

### Supported types and future collections

The current DAO registry supports Loco, Car, and MOW. Signals, turnouts, and
active motorized trackside equipment are fixed layout assets and intentionally
do not belong to `Roster`; a future `Layout` collection will operate over
those elements.

`ops.py` contains only supporting mechanics: ID validation, type resolution,
DAO selection, loading, and saving. It is not a public type-specific API.

## Consequences

- Every supported movable asset uses the same public operation model.
- Retired records remain historically retrievable without polluting operational
  searches.
- UI adapters can be added independently of the domain and persistence code.
- New movable entity types require a DAO registry entry, not a new operations
  facade.
- CLI commands will call this API; they must not duplicate its lifecycle or
  persistence behavior.

## Command-line adapter

The command-line adapter is available through:

```text
python -m railroad.operation.cli [--config PATH] COMMAND
```

Its commands map directly to the operating functions:

```text
view ID
retire ID
update ID (--input PATCH.json | --set ATTRIBUTE=VALUE [--set ATTRIBUTE=VALUE ...])
create --type {loco,car,mow} [--input OBJECT.json]
search [--where PATH=VALUE]
```

`create` builds a valid default object for its requested type when no input is
provided. When an input JSON object is supplied, it patches those defaults
before creation; identity remains assigned by `Asset.create`. `update` applies
either a JSON object patch or dotted `--set` assignments to an existing bound
asset before calling `asset.update()`. This keeps complex model data out of
long command-line flag lists while allowing small direct corrections.
