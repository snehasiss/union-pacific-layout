# Union Pacific HO scale layout project

---

_This repository is the authoritative digital representation of a physical Union Pacific HO scale model railroad. It contains the engineering documentation, software, configuration, operational procedures, and inventory necessary to reproduce the layout in whole or in part. The physical railroad is the deployed system; this repository is its source of truth._

### Under construction:
#### This project has started and is currently under development as the physical layout is under construction.
---

<pre><code>
union-pacific-layout/

README.md

config/                 # Application config JSON
data/                   # JSON representation of all railroad assets
docs/                   # Engineering documentation
inventory/              # Physical assets and procurement
operations/             # Deployment and maintenance procedures
resources/              # Photos, drawings, diagrams
resources/reference/    # External manuals and prototype information
src/                    # Firmware, Python, AI, utilities
tests/                  # Validation, simulations, and hardware tests
tools/                  # Generators, converters, and automation scripts
</code></pre>
---

### Roadmap:
Here is the [Roadmap document]{docs/designs/080-roadmap.md} to know more about the objective or intent and tentative final destination of this project.


### Current Directory Structure:
```
union-pacific-layout/
├── config
├── data
│   ├── car
│   ├── loco
│   ├── mow
│   ├── signal
│   └── turnout
├── docs
│   ├── dcc
│   ├── decisions
│   └── designs
├── inventory
│   ├── electronics
│   ├── locomotives
│   ├── rolling-stock
│   └── track
├── operations
│   └── jmri
├── resources
│   ├── drawings
│   ├── photos
│   └── references
├── src
│   ├── esp32
│   │   ├── device
│   │   ├── signal
│   │   ├── tests
│   │   └── turnout
│   ├── railroad
│   │   ├── dao
│   │   ├── domain
│   │   ├── infra
│   │   ├── operation
│   │   ├── rs
│   │   ├── service
│   │   ├── tests
│   │   │   ├── dao
│   │   │   ├── domain
│   │   │   ├── rs
│   │   │   └── tools
│   │   └── tools
│   │       └── imports
│   └── sbc
│       ├── dcc
│       ├── jmri
│       ├── service
│       └── tests
└── tmp
```

Continued...