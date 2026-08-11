# ADR-005: Software Architecture — Locomotive Domain Model

- **Status:** Accepted
- **Date:** 2026-08-11
- **Decision:** Implement the locomotive domain model, roster, and persistence foundation before introducing services or additional railroad entities.

## Context

The Union Pacific HO Scale Railroad project needs a digital representation of the physical locomotive collection.

The historical locomotive data is maintained in a spreadsheet and exported to CSV. The CSV files are an input/data-source representation rather than the domain model itself.

The current implementation phase is deliberately limited to:

- Locomotive domain objects
- Roster
- Locomotive persistence
- Import tooling required to populate the domain objects

The following architectural areas are intentionally deferred:

- `services/`
- `factory/`
- Cars
- Signals
- Turnouts
- Layout objects
- Operations
- Agentic/autonomous control

The source spreadsheet/CSV will be manually curated. Historical spelling, capitalization, and missing-data issues will be corrected or enriched in the source data before import. The importer should therefore not accumulate special-case corrections for known historical data-entry mistakes.

## Decision

### 1. Source data and domain model are separate

CSV is an external/input representation.

The domain model must not mirror the CSV schema merely because a field exists in the source file.

The intended flow is:

```text
Spreadsheet
    |
    | manual correction / historical enrichment
    v
CSV
    |
    | import
    v
Domain objects
    |
    v
Persistence
    |
    v
JSON
```

Source-data cleanup such as spelling mistakes, capitalization inconsistencies, and missing historical information will be handled in the spreadsheet/source CSV.

Domain-level invariants and semantics remain the responsibility of the domain classes.

### 2. Current source layout

The implementation will use the following top-level structure under `src`:

```text
src/
├── domain/
├── persistence/
├── tools/
└── tests/
```

`services/` and `factory/` are intentionally omitted from the current implementation phase.

The import tooling remains under:

```text
src/tools/imports/
```

The source CSV files currently provide separate steam and diesel datasets because their historical spreadsheet schemas differ.

### 3. Locomotive is the common domain entity

Steam and diesel locomotives are represented by a single `Locomotive` domain class.

Inheritance such as:

```text
Locomotive
├── SteamLocomotive
└── DieselLocomotive
```

is intentionally not used.

The domain is kept simple through composition.

A locomotive contains:

```text
Locomotive
├── Identity
├── Type
├── Prototype
├── Model
├── Electronics
└── Ownership
```

### 4. Locomotive type

The locomotive type is a first-class domain attribute:

```text
steam
diesel
```

There will be no electric locomotive type in the current domain model or planned scope.

`LocomotiveType` should be represented as a controlled domain value, preferably an enum.

```text
LocomotiveType
├── STEAM
└── DIESEL
```

### 5. Identity

Every locomotive has a persistent digital entity identity.

```text
Identity
├── id
├── railroad
├── reporting_mark
└── road_number
```

The `id` is independent of the prototype's railroad identity.

For example:

```text
id              = L001
railroad        = UP
reporting_mark  = UP
road_number     = 4014
```

The domain ID identifies the digital entity in this project, while the railroad/reporting-mark/road-number combination identifies the corresponding real-world locomotive.

### 6. Locomotive ID convention

Locomotive IDs use the prefix `L` followed by a sequential numeric identifier.

Examples:

```text
L001
L002
L003
...
L999
L1000
```

Three digits are preferred, with four digits supported if ever required.

The numeric sequence is persistent and is not an array index.

Once assigned, an ID must not change.

If `L002` is retired or removed, a later locomotive must not be renumbered to `L002`.

The ID is also the basis for the persistence filename:

```text
L001.json
L002.json
...
```

The ID generator should be generic in design, while the current entity namespace is `L` for locomotives.

When loading an existing persisted entity, the persisted ID is retained; a new ID is generated only for a genuinely new entity.

### 7. Prototype

`Prototype` represents the real-world locomotive rather than the physical HO model.

```text
Prototype
├── builder
├── model
├── nickname
└── purpose
```

#### Prototype model

The generic `model` attribute is deliberately used for both steam and diesel.

This is an important normalization decision.

For diesel locomotives, examples include:

```text
GP30
SD70ACe
SD90MAC
AC4400CW
```

For steam locomotives, examples include:

```text
4-6-6-4
4-8-8-4
4-8-4
2-8-8-0
2-10-2
```

The `prototype.model` field therefore represents the primary prototype classification/model by which a locomotive is identified.

This avoids having separate fields such as:

```text
diesel.loco_model
steam.wheel_arrangement
```

and allows common roster functionality such as listing or searching all unique prototype models without knowing whether the locomotive is steam or diesel.

There is intentionally **no separate `wheel_arrangement` attribute** in the domain model.

For steam locomotives, the wheel arrangement is the value of `prototype.model`.

#### Prototype nickname

`nickname` holds commonly used names such as:

```text
Big Boy
Challenger
Centennial
Bull Moose
```

The nickname is optional.

#### Prototype purpose

`purpose` represents the primary prototype purpose/classification.

Current controlled values are:

```text
passenger
freight
switcher
```

This applies primarily to diesel but is also applicable to steam.

`purpose` represents the primary classification rather than a complete historical service record. A locomotive's historical changes in assignment or service will be modeled separately in the future if required.

### 8. HO Model

`Model` represents the physical scale model owned by the project.

```text
Model
├── scale
├── manufacturer
└── product
```

The distinction is:

```text
Prototype = real-world locomotive
Model     = physical model of that locomotive
```

#### Scale

The project is an HO scale railroad.

`Model.scale` is initialized when the model object is created and is immutable for the lifetime of that model object.

The initial/default value is:

```text
HO
```

The implementation may use a controlled `Scale` enum even though only `HO` is currently required.

#### Manufacturer and product

`manufacturer` and `product` are assigned from the curated data source and may be populated after initial object creation.

For example:

```text
scale        = HO       # fixed at creation
manufacturer = BLI      # may be assigned later
product      = 4801     # may be assigned later
```

Only `scale` is immutable at the object level.

### 9. Electronics

Electronics represent the installed/associated model electronics rather than prototype characteristics.

The initial domain structure is:

```text
Electronics
├── dcc
├── sound
├── smoke
├── decoder
└── address
```

These attributes are intentionally separate from `Model` because electronics may be changed without changing the physical model identity.

### 10. Ownership

Ownership/purchase information is represented separately from the prototype and model identity.

The initial structure is:

```text
Ownership
├── status
├── store
├── price
└── acquired
```

Historical purchasing information may be enriched from sources such as eBay, TrainWorld, Lombard Hobbies, and other retailers before being committed to the source spreadsheet/CSV.

### 11. Roster

`Roster` is a domain collection of `Locomotive` entities.

It is not merely an exposed Python list.

The roster will eventually support operations such as:

```text
add()
remove()
find()
find_by_id()
find_by_reporting_mark()
find_by_prototype_model()
find_by_type()
find_by_purpose()
unique_prototype_models()
iteration
length
```

The roster must preserve the persistent identity of its locomotives.

### 12. Persistence

Persistence is separated from the domain.

The domain classes must not contain JSON or filesystem-specific persistence logic.

The intended boundary is:

```text
Domain object
    |
    v
Repository
    |
    v
JSON file
```

Locomotive persistence uses the locomotive ID as the filename:

```text
L001 -> L001.json
```

The repository is responsible for loading and saving domain objects.

The persisted JSON should contain the complete domain representation necessary to reconstruct the locomotive without generating a new ID.

### 13. Testing

Tests are colocated under `src/tests` as part of the current project structure:

```text
src/
├── domain/
├── persistence/
├── tools/
└── tests/
```

The initial implementation/testing sequence is:

1. `LocomotiveType`
2. `Identity`
3. `Prototype`
4. `Model`
5. `Electronics`
6. `Ownership`
7. `Locomotive`
8. `Roster`
9. JSON locomotive persistence
10. Import tooling integration

Each class should be implemented and tested before moving to the next significant layer.

## Consequences

### Positive

- Steam and diesel are represented uniformly.
- Roster queries do not need steam/diesel-specific logic for prototype classification.
- Prototype information is clearly separated from the physical HO model.
- Persistent locomotive IDs provide stable references for future systems.
- JSON filenames naturally map to domain entities.
- Source-data cleanup remains a one-time data-curation activity rather than becoming importer logic.
- The architecture remains simple and avoids premature inheritance or service/factory abstractions.
- The model can later be extended to cars, signals, turnouts, and other railroad entities using the same architectural principles.

### Trade-offs

- The source CSV schema and domain schema will not be identical.
- Some import mapping logic will be necessary when converting source records into domain objects.
- `prototype.model` has a different semantic representation for steam and diesel, although its domain meaning remains consistent: the primary prototype classification/model.
- Persistent ID allocation requires care to ensure IDs are never reused.

## Resulting Initial Domain Vocabulary

The first implementation will establish these domain types:

```text
LocomotiveType
Purpose
Scale

Identity
Prototype
Model
Electronics
Ownership

Locomotive
Roster
```

No inheritance hierarchy for steam/diesel is required.

No `services/` or `factory/` implementation is required at this stage.

## Example

A steam locomotive:

```json
{
  "identity": {
    "id": "L001",
    "railroad": "UP",
    "reporting_mark": "UP",
    "road_number": 4014
  },
  "type": "steam",
  "prototype": {
    "builder": "ALCO",
    "model": "4-8-8-4",
    "nickname": "Big Boy",
    "purpose": "freight"
  },
  "model": {
    "scale": "HO",
    "manufacturer": "Athearn",
    "product": "..."
  }
}
```

A diesel locomotive:

```json
{
  "identity": {
    "id": "L011",
    "railroad": "UP",
    "reporting_mark": "UP",
    "road_number": 7082
  },
  "type": "diesel",
  "prototype": {
    "builder": "GE",
    "model": "AC4400CW",
    "nickname": null,
    "purpose": "freight"
  },
  "model": {
    "scale": "HO",
    "manufacturer": "...",
    "product": "..."
  }
}
```

These two entities have the same domain structure even though their prototype classification differs.

## Status

**Accepted and ready for implementation.**
