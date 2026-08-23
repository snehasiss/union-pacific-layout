# ADR-006 — Railroad Asset Data Model

- **Status:** Accepted
- **Date:** 2026-08-22
- **Decision:** Define the current railroad locomotive data model around Identity, Prototype, Model, Control, and Asset.
- **Scope:** Locomotives
- **Supersedes:** Earlier exploratory locomotive domain-model decisions where applicable

---

# 1. Context

The railroad application needs a domain model capable of representing the physical HO-scale locomotive collection, its prototype information, model information, control/electronics configuration, and procurement/ownership lifecycle.

The initial design evolved while implementing the locomotive domain classes and CSV import functionality.

A key observation is that different attributes have different lifecycles:

- Some attributes are effectively immutable once established.
- Some attributes change occasionally.
- Some attributes represent the current condition of the physical model.
- Some attributes represent the procurement and ownership lifecycle.
- Some attributes represent the locomotive's control/electronics configuration.

The model must also remain simple enough to support the current locomotive use case without prematurely designing a generalized model for wagons, tankers, coaches, or MOW equipment.

CSV files are considered **master-data import sources**. Operational changes will subsequently be made against the persisted JSON representation.

---

# 2. Decision

The locomotive domain model consists of five primary domain classes:

```text
Identity
Prototype
Model
Control
Asset
```

The broader railroad software architecture remains:
```text
railroad/
├── domain/
├── dao/
├── rs/
├── tools/
└── tests/
```

The five domain classes have distinct responsibilities.

# 3. Domain Model
## 3.1 Identity
`Identity` establishes the identity of the physical railroad asset within the application.
Typical attributes include:

+ `id`
+ `entity_type`
+ `railroad`
+ `reporting_mark`
+ `road_number`

`Identity` should normally remain stable throughout the life of the record.

For example:
```
id = L341
reporting_mark = UP
road_number = 1203
```
The application identity is independent of the manufacturer's product identity.

## 3.2 Prototype
`Prototype` describes the real-world railroad locomotive represented by the model.
Typical attributes include:
+ `builder`
+ `model`
+ `nickname`
+ `purpose`
For steam locomotives, the prototype model may be represented by the wheel arrangement.

Examples:
```
4-8-8-4
4-6-6-4
4-8-2
```
For diesel locomotives, the prototype model may be represented by the manufacturer's model designation.

Examples:
```
SD40-2
GP30
H10-44
```

The locomotive type remains associated with the prototype/domain definition rather than being treated as a property of the physical HO model.

---

## 3.3 Model
`Model` describes the actual physical HO-scale model in the collection.

The current model attributes are:
```
manufacturer
scale
product
state
notes
```

### `manufacturer`
The manufacturer of the physical model.

Examples:
```
Broadway Limited
Athearn
Atlas
Bowser
```

### `scale`


The model scale.

The current railroad project is HO scale.

### `product`
A string containing useful product/model information supplied by the manufacturer or retailer.

This deliberately remains a string rather than becoming a detailed product sub-model at this stage.

### `state`
The current physical/service state of the model.

See `ModelState` below.

### `notes`
Free-form notes concerning the physical model.

This provides a place for model-specific observations without adding additional specialized attributes prematurely.

---

## 3.4 ModelState

`ModelState` represents the current state of the physical model.

The values are:

Value	Meaning

---

`ACTIVE`	Model is available for normal operation and is on the layout/roster duty.

---

`OFFLINE`	Model is temporarily unavailable for operation, for example because of maintenance, cleaning, decoder installation/programming, repair, or other work.

---

`STORED`	Model is physically owned but kept in storage, such as a box, cabinet, shelf, or other storage location, and is not currently in service.

---

`RETIRED`	Model has permanently been removed from active service/roster, whether retained as a spare, discarded, or otherwise no longer intended for operation.

---

The distinction between `ModelState` and `AssetStatus` is intentional.

For example:
```
asset.status = OWNED
model.state  = OFFLINE
```
means that the locomotive is owned but currently unavailable for operation.

---

### 3.5 Control






















