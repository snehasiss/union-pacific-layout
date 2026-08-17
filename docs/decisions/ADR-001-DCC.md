# ADR-001 — Digital Command Control Architecture

**Status:** Accepted  
**Date:** 2026-08-17  
**Scope:** DCC, locomotive control, power distribution, accessory control, supervisory control and autonomous operation

---

## 1. Context

The Union Pacific HO Scale Railroad is being designed as a long-lived, expandable model railroad with two complementary objectives:

1. Maintain a serious collection of prototypically appropriate Union Pacific locomotives and rolling stock and operate them realistically.
2. Build a modern, distributed control system capable of autonomous mainline operation while retaining manual control of yards and locomotive servicing areas.

The layout is expected to have:

- 200+ ft of running track.
- A folded-dogbone mainline with an upper continuous-running level.
- A lower-tier yard.
- Steam roundhouse / locomotive servicing area.
- Diesel servicing area.
- A possible hilly branchline area suitable for geared locomotives such as Shay, Climax and Heisler.
- Up to approximately 20 locomotives physically active on the railroad at a time.
- Approximately 10 locomotives operating simultaneously, with the remainder parked or being serviced.
- A large overall locomotive collection, including 100+ Union Pacific diesels, many equipped with ESU LokSound or SoundTraxx Tsunami decoders.
- A mixture of sound DCC, non-sound DCC and future DCC-equipped locomotives.

The railroad therefore requires a DCC architecture that is reliable, expandable, network-capable, compatible with JMRI, suitable for multiple power districts and boosters, independent of proprietary accessory-decoder ecosystems where practical, and capable of eventually supporting autonomous operation.

---

## 2. Decision

The railroad will use **DCC-EX as the primary Digital Command Control platform**, initially based on an **EX-CSB1 Express Commander Command System** with a regulated 15 V / 5 A power supply.

The DCC system will be treated as a **locomotive command and track-power subsystem**, rather than as the central architecture for every railroad function.

The broader system will be divided into distinct layers:

```text
                    Supervisory / Automation SBC
                  (Cubietruck initially; later
                   Raspberry Pi 5 / Vicharak Axon)
                              |
                         JMRI / Services
                              |
                        MQTT Message Bus
                              |
             +----------------+----------------+
             |                                 |
      ESP32 Distributed Nodes             DCC-EX
      Signals / Turnouts /                Locomotives /
      Detection / I/O                     Track Power
             |                                 |
             +------------- Railroad ----------+
```

### Primary responsibilities

**DCC-EX**

- Generate DCC packets.
- Control locomotives and locomotive functions.
- Provide the DCC programming interface.
- Provide track power through boosters and associated power districts.
- Provide the network interface used by JMRI and throttles.

**JMRI / Supervisory SBC**

- Provide the principal railroad operating interface.
- Manage locomotive roster and decoder configuration.
- Provide WiThrottle / user interfaces.
- Implement route, signalling and automation logic as the system evolves.
- Coordinate autonomous mainline operation.
- Interface between the DCC subsystem and the distributed accessory system.

**MQTT**

- Act as the event/message bus for the distributed accessory and automation system.
- Carry state and event information between the SBC, JMRI, ESP32 nodes and future services.
- Keep accessory control independent from DCC packet traffic where practical.

**ESP32 / Arduino nodes**

- Provide distributed local I/O.
- Control Tortoise motors and other turnouts.
- Drive signals and indicator LEDs.
- Read occupancy, sensors and other physical inputs.
- Perform deterministic local hardware functions.
- Communicate with the supervisory system over the IP network.

---

## 3. Initial DCC Hardware

The first implementation will consist of:

- One EX-CSB1.
- One regulated 15 V / 5 A power supply.
- One enclosed EX-CSB1 installation.

Initial operation will deliberately remain simple.

The first objective is to commission the EX-CSB1, connect it to the network, operate locomotives, and become familiar with DCC-EX before introducing additional boosters, power districts or automation.

---

## 4. Booster and Power-District Strategy

The system is designed to expand beyond the initial EX-CSB1.

The current conceptual target is:

### Booster 1

Approximately 5 A total capacity, divided into independently protected districts such as:

- Yard.
- Steam roundhouse.
- Diesel servicing area.
- Optional fourth district for the hilly / branchline area.

### Booster 2

Approximately 5 A total capacity, with districts such as:

- East UP mainline.
- East DOWN mainline.
- North UP mainline.
- North DOWN mainline.

The exact district boundaries will be finalized after the physical track plan and electrical load measurements are established.

The design principle is:

> **Boosters provide additional current capacity; circuit breakers provide isolation between districts.**

Individual power districts should have their own appropriately rated electronic circuit breaker / auto-reverser protection as required by the final track topology.

A short circuit in one protected district should therefore disconnect only that district rather than unnecessarily bringing down the entire railroad.

---

## 5. EX8874 Decision

The EX8874 Motor Shield is **not a required component of the initial architecture**.

The initial purchase will therefore be an EX-CSB1 with its enclosure, without assuming that an EX8874 will later be installed in the same enclosure.

If additional DCC capacity is required, the preferred expansion path will initially be to add another EX-CSB1 configured as a booster, rather than automatically adding an EX8874.

The EX8874 may still be used in the future if its particular hardware configuration, physical packaging, motor-driver arrangement or other capabilities provide a meaningful advantage.

This decision will be revisited only after real-world measurements demonstrate a requirement.

---

## 6. Power-District Isolation

Power districts will be electrically isolated from one another.

The intended topology is:

```text
                    Booster 1
                       |
              +--------+--------+
              |        |        |
            Yard     Steam    Diesel
              |        |        |
            CB-1     CB-2     CB-3


                    Booster 2
                       |
          +------------+------------+
          |            |            |
       East UP      East DOWN    North UP
          |            |            |
        CB-4         CB-5         CB-6

                       +
                  North DOWN
                       |
                     CB-7
```

Each district will have its own feeder wiring and protection.

Rail gaps / isolation boundaries will be used where required to prevent a fault in one district from propagating into another.

The final implementation will also ensure that adjacent districts are correctly phase-aligned to avoid shorts when locomotives or rolling stock bridge boundaries.

---

## 7. Accessory Architecture

Turnouts, signals and other accessories will **not be required to use individual DCC accessory decoders**.

Instead, the preferred architecture is:

```text
             JMRI / Automation
                     |
                MQTT / IP
                     |
              ESP32 Controller
                /    |     \
               /     |      \
        Tortoise   Signals   Sensors
```

This approach is intentional.

DCC is primarily responsible for locomotive control and track power. Accessory control is treated as a distributed IoT-style subsystem.

Advantages include:

- Reduced DCC traffic.
- Lower accessory cost.
- Geographic distribution of I/O.
- Local control close to physical devices.
- Easier expansion.
- Easier diagnostics.
- Independence from proprietary accessory-decoder addressing.
- Ability to expose accessory state through MQTT.
- Ability to integrate future automation and AI services.

Commercial DCC accessory decoders may still be used where they provide a clear practical advantage.

---

## 8. Network Architecture

The railroad will use the existing home IP network as the preferred infrastructure network.

The intended topology is:

```text
                    Home Network
                  Ethernet / Wi-Fi
                         |
        +----------------+----------------+
        |                |                |
      iPhone             SBC             ESP32
        |                |                |
      JMRI            MQTT/JMRI        I/O Nodes
                         |
                      DCC-EX
```

The EX-CSB1, SBC, iPhone and ESP32 devices should therefore communicate through the normal IP infrastructure rather than requiring every client device to establish a direct peer-to-peer connection to the EX-CSB1.

The home network remains responsible for IP connectivity. Internet access is not a functional requirement for railroad operation.

The railroad should continue to operate locally if the external Internet connection is unavailable.

---

## 9. Supervisory Computer

The initial supervisory environment will use the existing **Cubietruck running Ubuntu Linux** for familiarisation and early development.

The Cubietruck is considered a development / experimental platform rather than the final production platform.

The eventual production platform will be selected based on observed JMRI and automation requirements. Candidates include:

- Raspberry Pi 5 with 8 GB RAM.
- Vicharak Axon.
- Another suitable Linux SBC if future requirements justify it.

The software will preferably be installed **natively on the SBC**, rather than using Docker or another container platform.

The system is a single-instance physical installation; container orchestration is therefore not considered necessary.

---

## 10. Software Architecture

The initial software stack is expected to include:

- Linux.
- OpenJDK 17 where required by the selected JMRI release.
- JMRI.
- MQTT broker (for example, Mosquitto).
- ESP32 firmware.
- Custom railroad automation services as required.

Services should preferably run as native Linux services managed by `systemd`.

Git will be used for configuration, firmware, documentation and software source control.

---

## 11. Autonomous Operation

The long-term operating objective is:

> **Autonomous mainline operation with manual yard and locomotive-servicing operation.**

The intended separation is:

### Autonomous

- Mainline train movements.
- Block occupancy.
- Signal aspects.
- Route setting.
- Interlocking.
- Train spacing.
- Meets and overtakes.
- Dispatcher decisions.
- Automatic stopping and restarting.

### Manual

- Yard switching.
- Classification.
- Industrial switching.
- Steam roundhouse movements.
- Diesel servicing.
- Locomotive maintenance movements.
- Other local shunting activities.

The architecture must therefore support both human and automated control without requiring a fundamental redesign.

---

## 12. Future Expansion

The architecture should support future additions such as:

- Additional DCC boosters.
- Additional protected power districts.
- More ESP32 I/O nodes.
- Occupancy detection.
- Signal control.
- Route locking.
- Dispatcher panels.
- Web-based dashboards.
- Locomotive telemetry.
- Runtime and maintenance tracking.
- Automated scheduling.
- AI-assisted or AI-based dispatching.

Future autonomous or AI services must operate through defined software interfaces and should not directly bypass safety-critical local interlocking or electrical protection.

---

## 13. Alternatives Considered

### Commercial proprietary DCC command stations

Rejected as the primary platform because the project requires:

- Open integration.
- Expandability.
- IP/network access.
- JMRI integration.
- Future software and embedded-system experimentation.

Commercial systems remain possible for individual applications but are not the architectural foundation.

### DCC accessory decoders for every turnout and signal

Rejected as the default approach because the layout will contain a substantial number of physical accessories and the project explicitly intends to experiment with distributed ESP32 control.

### Single centralized accessory controller

Rejected as the long-term architecture because it creates excessive wiring between the control computer and geographically distributed railroad hardware.

### Docker / containerized deployment

Rejected for the initial and expected single-instance deployment because it adds operational complexity without providing a meaningful benefit for this physical installation.

---

## 14. Consequences

### Positive

- Open and expandable DCC platform.
- Clear separation between locomotive control and accessory control.
- Multiple power districts can be added as required.
- Accessory hardware can be distributed geographically.
- ESP32 provides inexpensive and flexible local I/O.
- MQTT provides an event-driven integration mechanism.
- JMRI provides a mature railroad control layer.
- The architecture supports both manual and autonomous operation.
- Hardware and software can evolve independently.

### Negative

- More engineering effort than using an integrated commercial DCC/accessory ecosystem.
- Multiple subsystems require careful configuration and documentation.
- MQTT, ESP32 firmware and JMRI introduce additional software components.
- Electrical isolation and power-district design require disciplined wiring.
- Autonomous operation will require substantial later development and testing.

---

## 15. Validation Plan

### Stage 1

EX-CSB1 successfully operates one or more locomotives.

### Stage 2

JMRI communicates reliably with DCC-EX and provides locomotive control.

### Stage 3

ESP32 communicates with the MQTT broker and controls a simple output.

### Stage 4

ESP32 controls a turnout and/or signal.

### Stage 5

Occupancy detection is integrated.

### Stage 6

JMRI coordinates DCC locomotive movement with signals, turnouts and occupancy.

### Stage 7

A train completes an autonomous mainline route.

### Stage 8

Autonomous mainline operation and manual yard operation coexist safely.

---

## 16. Review Criteria

This ADR should be revisited if any of the following occur:

- DCC current requirements materially exceed the planned booster capacity.
- A different booster architecture provides a significant reliability or cost advantage.
- JMRI performance exceeds the practical capability of the selected SBC.
- MQTT proves unsuitable for the required accessory latency or reliability.
- ESP32 controllers prove inadequate for required I/O or safety functions.
- The layout's physical track plan requires a substantially different power-district topology.
- Autonomous operation introduces requirements not satisfied by the current architecture.

---

## 17. Final Decision Statement

The Union Pacific HO Scale Railroad will use **DCC-EX as the locomotive and track-power control foundation**, with **EX-CSB1 as the initial command station**.

The railroad will evolve toward a **distributed control architecture** in which:

- DCC-EX controls locomotives and track power.
- JMRI provides railroad operating and automation logic.
- MQTT provides event-driven communication.
- ESP32 nodes provide distributed physical I/O.
- A Linux SBC provides supervisory control and autonomous-operation services.
- Multiple boosters and independently protected power districts provide electrical scalability.

The architecture deliberately separates **railroad control logic from physical I/O and DCC packet generation**, allowing the system to grow from a simple manually operated DCC railroad into an autonomous, software-controlled railroad without requiring a fundamental architectural redesign.

---

## Related Documents

- `EngineeringNotebook.md`
- `ADR-002-JMRI.md` *(planned)*
- `ADR-003-Accessory-Control.md` *(planned)*
- `ADR-004-MQTT.md` *(planned)*
- `ADR-005-SoftwareArch.md`
- `docs/dcc-network.md`
- `docs/signalling.md`
- `docs/testing.md`
