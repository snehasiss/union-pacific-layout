# Engineering Notebook

**Project:** Union Pacific HO Scale Railroad
**Project Start:** 29 July 2026
**Version:** 0.1

---

# Vision

To design and build a prototypically accurate Union Pacific HO scale railroad that combines realistic operations with modern control system engineering.

The railroad will be based on an open, modular architecture using DCC-EX, JMRI and distributed ESP32-based controllers communicating over an MQTT message bus. The long-term objective is to support autonomous operation of mainline traffic while allowing manual operation of yard, locomotive servicing and industrial switching activities.

The project will be executed incrementally. Each subsystem will be validated independently before being integrated into the complete railroad.

This notebook records not only *what* was built, but also *why* each engineering decision was made.

---

# Engineering Principles

The project follows a few guiding principles.

* Prototype accuracy takes precedence over convenience.
* Build a reliable operating railroad before building scenery.
* Use open standards and open-source software wherever practical.
* Design for expansion rather than immediate completeness.
* Keep the architecture modular so individual subsystems can evolve independently.
* Document every significant engineering decision.

---

# Target System Architecture

```
                           Raspberry Pi 5
                                 │
                           OpenJDK + JMRI
                                 │
                           MQTT Message Bus
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
    Yard Controller        Mainline Controller     Branch Controller
       (ESP32)                 (ESP32)                (ESP32)
        │                        │                        │
   Turnouts                 Signals & Blocks        Accessories
        │                        │                        │
                     DCC-EX Command System
                                 │
                         Multiple Boosters
                                 │
                       Multiple Power Districts
                                 │
                      Union Pacific HO Railroad
```

---

# Development Roadmap

## Phase 1 – Digital Command Control Foundation

* Procure DCC-EX EX-CSB1 command station.
* Commission the command station.
* Verify locomotive operation.
* Configure Wi-Fi networking.
* Learn DecoderPro and WiThrottle.

## Phase 2 – Software Platform

* Install JMRI.
* Install OpenJDK 17.
* Configure Cubietruck as the initial development server.
* Evaluate migration to Raspberry Pi 5 for production deployment.

## Phase 3 – Distributed Control

* Develop ESP32 firmware.
* Establish MQTT communication.
* Prototype turnout and signal control.
* Validate communication architecture.

## Phase 4 – Railroad Automation

* Block occupancy detection.
* Route control.
* Signal logic.
* Dispatcher automation.
* Autonomous mainline train operation.

## Phase 5 – Physical Railroad

* Permanent benchwork.
* Track laying.
* Electrical distribution.
* Power districts.
* Scenery.
* Structures.
* Weathering.
* Operational refinement.

---

# Engineering Log

## 2026-07-29

### Milestone

Project initiated with the selection of the DCC-EX ecosystem as the foundation for the railroad control system.

### Procurement

Vendor: **store.dcc-ex.com**

| Item                                     | Cost (USD) |
| ---------------------------------------- | ---------: |
| EX-CSB1 Express Commander Command System |    $159.80 |
| Snap-fit enclosure                       |     $15.25 |
| Shipping                                 |     $19.15 |

Power Supply:

* 15 V / 5 A regulated supply

**Total Project Cost (Phase 1): US$194.20**

### Engineering Decision

After evaluating commercially available DCC systems, DCC-EX was selected because it provides:

* Open architecture
* Excellent integration with JMRI
* Expandable multi-booster capability
* Native support for modern IP networking
* Strong community support
* Ability to integrate with custom ESP32-based distributed controllers

The project intentionally avoids proprietary accessory ecosystems wherever practical.

### Immediate Objectives

1. Commission the EX-CSB1.
2. Install JMRI on the Cubietruck.
3. Verify OpenJDK 17 compatibility.
4. Connect using WiThrottle.
5. Read and program locomotive decoders.
6. Familiarise with the DCC-EX software ecosystem.

### Long-Term Vision

The completed railroad should operate as a distributed control system rather than a conventional DCC layout.

Locomotives will be controlled through DCC-EX, while accessories, signalling, occupancy detection and automation will be coordinated through JMRI and distributed ESP32 controllers communicating over MQTT.

The ultimate operational objective is to allow autonomous operation of Union Pacific mainline traffic while retaining manual control of yards, engine terminals and servicing facilities to provide an engaging and prototypical operating experience.

---

*"A reliable railroad begins with a reliable architecture."*

