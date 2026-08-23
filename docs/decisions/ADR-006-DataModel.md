# ADR-006: Railroad Asset Data Model

- **Status:** Accepted
- **Date:** 2026-08-23
- **Decision:** Finalize the current domain data model before implementing operational JSON functions.

## 1. Context

The railroad application initially evolved around locomotives, but the architecture is intended to support the broader railroad domain: locomotives, cars, MOW equipment, signals, turnouts, and other railroad assets.

The data model therefore separates:

- the **domain** classification of an entity;
- its **identity**;
- the **prototype** represented by the model;
- the physical **model** owned or tracked by the application;
- **control** information for powered models;
- **asset** information describing acquisition and ownership.

A deliberate distinction is also made between:

- `asset.status` — the acquisition/ownership lifecycle of the physical model; and
- `model.status` — the operational condition of the physical model.

These two states describe different concerns and must not be conflated.

CSV files are treated as **master-data import sources**. JSON files are the persistent operational representation. Future functionality will update JSON transactionally without requiring the original CSV to change.

## 2. Decision

The domain model is organized into the following layers:

```text
domain
├── identity
├── prototype
├── model
├── control
└── asset
```

Rolling-stock-specific classifications remain outside `prototype`:

```text
rs
├── loco.py
├── car.py
└── mow.py
```

Each rolling-stock class owns its own type enumeration.

For example:

```text
LocoType
    STEAM
    DIESEL
    TURBINE
    ...

CarType
    WAGON
    HOPPER
    TANKER
    INTERMODAL
    ...

MOWType
    ...
```

`Prototype.type` identifies the broad railroad entity category, while the corresponding rolling-stock class provides the more specific type.

For example:

```text
prototype.type = LOCO
loco.type       = STEAM
```

This prevents `Prototype` from becoming contaminated with locomotive-, car-, or MOW-specific classifications.

## 3. Model Structure

### 3.1 Identity

`Identity` provides the persistent identity of a railroad entity.

Responsibilities:

- persistent application ID;
- entity type;
- railroad;
- reporting mark;
- road number;
- validation of identity invariants;
- generation and observation of persistent IDs.

Example:

```json
{
    "id": "L001",
    "entity_type": "loco",
    "railroad": "union pacific",
    "reporting_mark": "UP",
    "road_number": "4014"
}
```

`IdGenerator` maintains sequential IDs within an entity namespace:

```text
L001, L002, ...
C001, C002, ...
M001, M002, ...
```

### 3.2 Prototype

`Prototype` describes the real-world railroad prototype represented by the model.

Responsibilities:

- broad prototype/entity classification;
- prototype builder;
- prototype model;
- nickname;
- intended purpose.

The prototype is intentionally independent of the physical model maker.

Examples:

```text
builder = ALCo
model   = 4-8-8-4
```

or:

```text
builder = EMD
model   = SD70ACe
```

### 3.3 Model

`Model` describes the physical scale model.

Responsibilities:

- model maker;
- scale;
- product information;
- operational state.

The maker is the manufacturer of the **model**, not the builder of the real prototype.

Therefore:

```text
prototype.builder = ALCo
model.maker       = Athearn
```

The current model attributes are:

| Attribute | Responsibility |
|---|---|
| `maker` | Manufacturer/model maker |
| `scale` | Scale of the physical model |
| `product` | Product/model details |
| `status` | Operational state of the physical model |

#### ModelStatus

`ModelStatus` represents the current physical/operational state of the model.

| Value | Meaning |
|---|---|
| `UNKNOWN` | Model state is not known or is not applicable because the physical model has not been obtained |
| `ACTIVE` | Model is on the layout and available for service |
| `OFFLINE` | Model is temporarily unavailable for service, e.g. maintenance, cleaning, decoder programming, or repair |
| `STORED` | Model is physically possessed but kept in storage/off the layout |
| `RETIRED` | Model has permanently been removed from active service or the roster |

`UNKNOWN` is important when `asset.status` is anything other than `OWNED`, because the application does not possess the physical model and therefore cannot meaningfully assert its physical operational state.

### 3.4 Control

`Control` describes how a powered model is controlled.

Responsibilities:

- control type;
- lighting capability;
- sound capability;
- smoke capability;
- decoder;
- decoder address.

The primary control transition is:

```text
DC
 ↓
decoder installation/programming
 ↓
DCC
```

Control information is therefore relatively stable but may change when the physical model is modified.

For a DC locomotive:

```text
control.type = DC
control.decoder = null
```

For a DCC locomotive:

```text
control.type = DCC
control.decoder = ...
control.address = ...
```

### 3.5 Asset

`Asset` describes acquisition and ownership information for the physical model.

Responsibilities:

- acquisition status;
- source/store;
- purchase price;
- acquisition date.

#### AssetStatus

`AssetStatus` represents the acquisition/ownership lifecycle.

| Value | Meaning |
|---|---|
| `TARGET` | A specific model has been identified as a future acquisition target |
| `INTENT` | The model is intended for procurement |
| `SHIPPED` | The model has been purchased and is currently in transit |
| `PARKED` | The model has been purchased and delivered to an intermediate location, but is not yet in the user's possession |
| `OWNED` | The model has been obtained and is in the user's possession |

`TARGET` replaces the earlier concept of `IDENTIFIED`/`SPOTTED`.

The distinction between `SHIPPED` and `PARKED` is intentional. A model may have already been purchased and received at a trusted intermediate address while still awaiting physical transfer to the owner.

## 4. Relationship Between Asset Status and Model Status

`asset.status` and `model.status` represent independent dimensions.

### Acquisition lifecycle

```text
TARGET
   ↓
INTENT
   ↓
SHIPPED
   ↓
PARKED
   ↓
OWNED
```

### Physical model lifecycle

```text
UNKNOWN
   ↓
STORED ↔ OFFLINE ↔ ACTIVE
                ↓
             RETIRED
```

The model state becomes meaningful only when the physical model is available.

Typical examples:

| Asset Status | Model Status | Interpretation |
|---|---|---|
| `TARGET` | `UNKNOWN` | Model identified as a future target; not owned |
| `INTENT` | `UNKNOWN` | Procurement planned; model not possessed |
| `SHIPPED` | `UNKNOWN` | Purchased and in transit |
| `PARKED` | `UNKNOWN` | Purchased and received elsewhere, awaiting possession |
| `OWNED` | `STORED` | Model possessed but stored |
| `OWNED` | `OFFLINE` | Model possessed but temporarily unavailable |
| `OWNED` | `ACTIVE` | Model available for layout operation |
| `OWNED` | `RETIRED` | Model permanently removed from service |

This separation prevents acquisition state from being confused with physical operating condition.

## 5. Rolling Stock Classification

The broad classification belongs to the prototype/domain layer.

```text
Prototype.type
    LOCO
    CAR
    MOW
    SIGNAL
    TURNOUT
    ...
```

The detailed type belongs to the corresponding entity under `rs`.

### Locomotive

```text
Prototype.type = LOCO

LocoType
    STEAM
    DIESEL
    TURBINE
    ...
```

### Car

```text
Prototype.type = CAR

CarType
    WAGON
    HOPPER
    TANKER
    INTERMODAL
    ...
```

### MOW

```text
Prototype.type = MOW

MOWType
    ...
```

This structure allows new rolling-stock classifications to evolve without modifying the generic `Prototype` model.

## 6. Master Data vs Transactional Data

The data model recognizes different rates of change among attributes.

### Mostly immutable

These describe what the entity fundamentally is:

- `Identity`
- `Prototype`

They normally do not change after creation.

### Occasionally mutable

These describe characteristics of the physical model and its configuration:

- `Model`
- `Control`
- `Asset`

Examples include:

```text
model.maker
model.product
model.scale
model.status

control.type
control.decoder
control.address

asset.status
asset.source
asset.price
asset.acquired
```

Some changes may occur only once or very rarely. For example:

```text
model.status = STORED
control.type = DC

        decoder installation

model.status = ACTIVE
control.type = DCC
```

### Operational data

The model currently keeps operationally changing information minimal. Where future requirements justify additional frequently changing attributes, they should be introduced deliberately rather than prematurely creating another abstraction.

## 7. CSV and JSON Responsibilities

CSV files are the source for **master record import**.

They provide the initial information required to construct domain objects.

The import flow is:

```text
CSV
 ↓
LocoImport
 ↓
Loco domain object
 ↓
LocoDAO
 ↓
JSON
```

The JSON representation is the persistent working representation of the application.

After import, operational functions will work against JSON/domain objects rather than treating the CSV as a transactional store.

Planned operational capabilities include:

- search;
- master-data edit;
- transactional update;
- retrieval;
- persistence.

## 8. Class Responsibilities

| Class | Location | Responsibility |
|---|---|---|
| `Identity` | `domain/identity.py` | Persistent entity identity and railroad identification |
| `IdGenerator` | `domain/identity.py` | Generate and observe sequential entity IDs |
| `EntityType` | `domain/identity.py` | Broad application entity classification |
| `Prototype` | `domain/prototype.py` | Real-world prototype information |
| `Purpose` | `domain/prototype.py` | Prototype purpose classification |
| `Model` | `domain/model.py` | Physical scale model information and operational state |
| `ModelStatus` | `domain/model.py` | Physical model state |
| `Control` | `domain/control.py` | DCC/DC and decoder-related control information |
| `ControlType` | `domain/control.py` | Control system classification |
| `Asset` | `domain/asset.py` | Acquisition and ownership information |
| `AssetStatus` | `domain/asset.py` | Acquisition/ownership lifecycle |
| `Loco` | `rs/loco.py` | Locomotive rolling-stock entity |
| `LocoType` | `rs/loco.py` | Locomotive-specific classification |
| `Car` | `rs/car.py` | Car rolling-stock entity |
| `CarType` | `rs/car.py` | Car-specific classification |
| `MOW` | `rs/mow.py` | Maintenance-of-way rolling-stock entity |
| `MOWType` | `rs/mow.py` | MOW-specific classification |
| `LocoDAO` | `dao/loco.py` | Persistence and retrieval of locomotive JSON |
| `IOStream` | `dao/iostream.py` | Generic filesystem I/O |
| `LocoImport` | `tools/loco_import.py` | Convert locomotive CSV records into `Loco` objects |
| `import_exec` | `tools/import_exec.py` | Execute discovery and import of railroad asset CSV files |

The naming convention intentionally follows the entity/tool relationship:

```text
Loco      ↔ LocoImport
Car       ↔ CarImport
MOW       ↔ MOWImport
Signal    ↔ SignalImport
Turnout   ↔ TurnoutImport
```

## 9. Intended Directory Structure

```text
src/
└── railroad/
    ├── domain/
    │   ├── __init__.py
    │   ├── identity.py
    │   ├── prototype.py
    │   ├── model.py
    │   ├── control.py
    │   └── asset.py
    │
    ├── rs/
    │   ├── __init__.py
    │   ├── loco.py
    │   ├── car.py
    │   └── mow.py
    │
    ├── dao/
    │   ├── __init__.py
    │   ├── iostream.py
    │   └── loco.py
    │
    ├── tools/
    │   ├── __init__.py
    │   ├── loco_import.py
    │   ├── import_exec.py
    │   └── imports/
    │       ├── steam.csv
    │       └── diesel.csv
    │
    └── tests/
        ├── domain/
        ├── rs/
        ├── dao/
        └── tools/
```

Persistent data is kept separately from source code:

```text
data/
└── loco/
    ├── L001.json
    ├── L002.json
    └── ...
```

All locomotive types—steam, diesel, and turbine—are persisted together under `data/loco/`.

## 10. Consequences

### Positive

- Acquisition status and physical model state are clearly separated.
- Generic prototype information remains independent of rolling-stock-specific classifications.
- Locomotive, car, and MOW types can evolve independently.
- CSV remains suitable for initial/master-data import.
- JSON becomes the persistent operational representation.
- The model is small enough to avoid premature abstractions.
- Future operational functionality can update individual aspects without redesigning the core domain.

### Trade-offs

- `asset.status` and `model.status` must be interpreted together when determining the complete lifecycle of a model.
- `UNKNOWN` is required as a meaningful placeholder for models not yet in possession.
- Some attributes that are currently modeled as occasional changes may later need more explicit transaction/history support.
- Additional rolling-stock types will require corresponding classes and enums under `rs`.

## 11. Implementation Guidance

The current implementation should preserve the separation established by this ADR.

In particular:

1. Do not move `LocoType`, `CarType`, or `MOWType` into `Prototype`.
2. Do not create separate modules such as `loco_type.py`, `car_type.py`, or `mow_type.py` merely for these enums.
3. Keep `ModelStatus` in `domain/model.py`.
4. Keep `AssetStatus` in `domain/asset.py`.
5. Use `maker` for the physical model manufacturer.
6. Use `builder` for the real-world prototype builder.
7. Use `TARGET` for an identified future acquisition target.
8. Treat CSV import as master-data initialization.
9. Treat JSON persistence as the operational data store.
10. Avoid introducing a separate `runtime` object unless future requirements demonstrate a real need for it.

## 12. Future Evolution

This ADR intentionally focuses on the current model and does not attempt to solve all future rolling-stock requirements.

As cars, MOW equipment, signals, turnouts, and other entities are implemented, their specific data models should be introduced within their respective areas without unnecessarily expanding the generic domain classes.

Operational history, audit trails, transaction records, and richer runtime information may be introduced later if the operational layer requires them.
