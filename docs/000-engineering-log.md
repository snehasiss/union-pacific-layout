# Engineering Notebook

| | |
|---|---|
| **Project** | Union Pacific HO Scale Railroad |
| **Project Start** | 29 July 2026 |
| **Version** | 0.1 |

---

# Engineering Log

## 25 July 2026

### Milestone

Started exploring a suitable DCC system for my layout, which is currently under construction.

Consulted ChatGPT extensively over multiple days regarding the architecture and selection process.

https://chatgpt.com/c/6a646941-70c8-83ee-a626-fd9a4bccfce1

Created this repository and its initial contents. This engineering notebook will continue to evolve as the railroad project progresses.

---

## 29 July 2026

### Milestone

Project officially initiated with the selection of the **DCC-EX** ecosystem as the foundation for the railroad control system.

### Procurement

| | |
|---|---|
| **Vendor** | `store.dcc-ex.com` |
| **Items Ordered** | • EX-CSB1 Express Commander Command System<br>• 15 V / 5 A regulated power supply<br>• Snap-fit enclosure |

---

### Engineering Decision

After evaluating commercially available DCC systems, **DCC-EX** was selected because it provides:

- Open architecture
- Excellent integration with JMRI
- Expandable multi-booster capability
- Native support for modern IP networking
- Strong community support
- Ability to integrate with custom ESP32-based distributed controllers

The project intentionally avoids proprietary accessory ecosystems wherever practical in order to maximize interoperability, maintainability, and future expansion.

---

### Immediate Objectives

- [ ] Commission the EX-CSB1
- [ ] Install JMRI on the Cubietruck
- [ ] Verify OpenJDK 17 compatibility
- [ ] Connect using WiThrottle
- [ ] Read and program locomotive decoders
- [ ] Familiarise with the DCC-EX software ecosystem

---

### System Vision

The long-term architecture can be summarized as

- Railroad
- DCC-EX
- JMRI
- ESP32 Distributed Controllers
- Automation

Future expansion will include multiple boosters, distributed accessory controllers, signalling, CTC, and autonomous train operations.

---

> *"A reliable railroad begins with a reliable architecture."*
