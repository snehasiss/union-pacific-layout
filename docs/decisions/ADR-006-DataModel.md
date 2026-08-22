# ADR-006 — Railroad Asset Data Model

- **Status:** Accepted
- **Date:** 2026-08-22
- **Decision:** Define the current railroad locomotive data model around Identity, Prototype, Model, Control, and Asset.
- **Scope:** Locomotives
- **Supersedes:** Earlier exploratory locomotive domain-model decisions where applicable

---

## 1. Context

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

railroad/
├── domain/
├── dao/
├── rs/
├── tools/
└── tests/
```