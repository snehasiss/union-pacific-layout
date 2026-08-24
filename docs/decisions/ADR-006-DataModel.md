# ADR-006: Railroad Asset Data Model and Operations

- **Status:** Accepted
- **Date:** 2026-08-24
- **Supersedes:** The acquisition/ownership and scale decisions in ADR-005

## Context

The application represents rolling stock and fixed railroad elements: locomotives, cars, MOW equipment, signals, turnouts, and future active trackside equipment. The earlier model split the lifecycle between `domain.Asset` acquisition data and `Model` operational data. That made the lifecycle ambiguous and reserved the useful name `Asset` for a narrow acquisition record.

The operation layer also needs one generic, framework-independent API. It must not grow separate operation facades for each concrete type.

## Decision

### Domain composition

Railroad domain entities are composed from common value objects:

```text
Identity + Prototype + Model + Control + entity-specific classification
```

`domain.Asset` and `AssetStatus` do not exist. `Asset` is reserved for the generic operational abstraction over any persisted railroad object.

`Model` contains the model and acquisition information:

| Attribute | Meaning |
|---|---|
| `maker` | Physical model manufacturer |
| `product` | Product/model details |
| `scale` | `Scale` enum value |
| `status` | Unified lifecycle `Status` |
| `source` | Identified source or seller |
| `price` | Purchase or listed price |
| `acquired` | Date physically or commercially acquired, when known |
| `note` | Free-form model note |

### Scale

The layout supports two compatible model scales on the same gauge track:

```python
from railroad.domain.model import Scale

Scale.HO  # default
Scale.OO  # British OO scale
```

`Model.scale` is mutable and defaults to `Scale.HO`. JSON persists the stable enum values as strings, `"HO"` and `"OO"`, and DAOs reconstruct the enum on read.

### Unified lifecycle

`Status` is the only lifecycle enum.

| Value | Meaning |
|---|---|
| `INTENT` | The model is known and one is intended for acquisition. |
| `SPOTTED` | A specific purchasable example or source has been identified. |
| `BOUGHT` | Purchase completed. |
| `SHIPPED` | Dispatched or in transit. |
| `PARKED` | Physically arrived, but not yet placed into normal storage. |
| `STORED` | Physically possessed and stored; an original box is not required. |
| `ACTIVE` | Operationally deployed. |
| `REPAIR` | Temporarily unavailable for operation. |
| `RETIRED` | Permanently removed from the collection. |
| `MISSED` | Acquisition failed, for example by refund, return, loss, or non-shipment; it may later return to `INTENT`. |

`RETIRED` objects remain persistent records. They are retrievable by ID but excluded from operational collections and searches.

### Operational API

The operation layer is framework-independent. Service adapters such as Flask, REST, and mobile interfaces belong under `railroad/service` later.

`Asset` is the generic, object-centric entry point:

```python
assets = Asset(config)

asset = assets.view("L001")  # retrieves an object even when retired
asset.model.note = "Decoder checked"
asset.update()
asset.retire()

created = assets.create(
    EntityType.LOCO,
    builder,
    railroad="Union Pacific",
    reporting_mark="UP",
    road_number="4014",
)
```

`ops.py` contains only supporting mechanics: ID validation, type resolution, DAO selection, object loading, and persistence. Do not introduce `LocoOps`, `CarOps`, `MowOps`, or equivalent per-type operation facades.

### Operational collections

`Roster` represents movable track vehicles that may occupy a track block:

```text
Loco, Car, MOW
```

`Roster.from_config(config)` loads the currently persisted vehicle types. `Roster.search(criteria)` searches an active roster and returns matching IDs only. A roster always excludes `RETIRED` objects.

Signals, turnouts, and active motorized trackside equipment are fixed layout elements, not roster members. A future `Layout` collection will track and search those assets separately.

## Persistence and migration

JSON is the operational persistence format. Current DAOs persist `Model` fields under `model`, including `scale` and `status`.

Existing legacy JSON may still contain a top-level `asset` object. It must be migrated safely by moving acquisition fields into `model`, translating legacy lifecycle values, and then rewriting the record only after migration tests cover the behavior. This migration is intentionally separate from the operational API change.

CSV remains a source for initial/master-data import; it is not the transactional operational store.

## Consequences

- Every railroad object can use the same operational abstraction.
- Acquisition and operational lifecycle are one explicit, auditable state.
- HO and OO models can coexist while remaining type-safe in Python and compatible in JSON.
- Block-occupying vehicles and fixed layout assets remain separate operational collections.
- Signals and turnouts can gain DAOs and `Layout` support without changing the roster contract.

## Implementation guidance

1. Keep `Scale` and `Status` in `domain/model.py`.
2. Keep `Model.scale` mutable and limited to `Scale.HO` and `Scale.OO`.
3. Preserve retired JSON records; never delete one merely because it is retired.
4. Keep public operations on `Asset` and collection searching on `Roster`.
5. Implement `Layout` separately for non-moving operational elements.
6. Add migration coverage before bulk rewriting legacy data.
