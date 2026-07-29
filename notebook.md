# Engineering Notebook

**Project:** Union Pacific HO Scale Railroad
**Project Start:** 29 July 2026
**Version:** 0.1

---

# Engineering Log

## 2026-07-25

### Milestone

Started exploring a suitable DCC system for my layout which is under construction.

Consulted chatgpt for a long time over multiple days. https://chatgpt.com/c/6a646941-70c8-83ee-a626-fd9a4bccfce1

Created this repository and the contents. This will keep getting updated as we progress.

$$
I = \int_{a}^{b} f(x) \,dx
$$


## 2026-07-29

### Milestone

Project initiated with the selection of the DCC-EX ecosystem as the foundation for the railroad control system.

### Procurement

Vendor: **store.dcc-ex.com**

Items: EX-CSB1 Express Commander Command System with 
  15 V / 5 A regulated power supply and
  Snap-fit enclosure                      

---

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

---

*"A reliable railroad begins with a reliable architecture."*

