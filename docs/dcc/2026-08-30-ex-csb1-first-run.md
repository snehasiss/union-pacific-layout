# EX-CSB1 Initial Commissioning and First Locomotive Run

**Date:** 2026-08-30  
**Milestone:** First successful DCC locomotive operation using the DCC-EX EX-CSB1

## Objective

Commission the new EX-CSB1 safely on a short, isolated HO-scale test track and prove the complete control path with one known-good DCC sound locomotive. JMRI, permanent layout wiring, accessory control, and CV changes were deliberately left for later stages.

## Equipment

- DCC-EX EX-CSB1 Express Commander in its snap-fit enclosure
- DCC-EX firmware 5.6.3
- Supplied power adapter:
  - 15 V DC
  - 6 A capacity
  - Centre-positive barrel connector
  - 100–240 V AC input
- Short, physically isolated section of HO track
- Twisted-pair temporary track feeder with alligator clips
- Rapido Trains product 48530:
  - HO GE 44-tonner
  - Union Pacific #903999
  - Factory ESU LokSound 5 sound decoder
  - MoPower uninterrupted-power system
- iPhone running WiThrottle Lite
- Intel iMac running Brave and DCC-EX EX-WebThrottle

The original project context described the supply as 15 V / 5 A. Inspection of the actual label established that the delivered adapter is rated at **15 V / 6 A**.

## Physical Inspection and Wiring

The EX-CSB1 board appeared undamaged and correctly seated in the enclosure base. The OLED protective film was left in place during testing.

The standard output configuration was confirmed as:

- **Output A:** MAIN
- **Output B:** PROG

The isolated test track was connected only to the upper blue terminal, output A. Output B remained physically unwired. No DC controller or other track-power source was connected. The unused alligator clips were kept away from the live track connections to prevent an accidental short.

## Electronics-Only Power-Up

The first startup was performed with both track outputs disconnected and without a locomotive load. The EX-CSB1 booted normally and displayed:

- DCC-EX version 5.6.3
- EXCSB1 hardware identification
- Two detected districts
- Track power off
- 0 mA track current
- Wi-Fi access-point information
- Output A configured as MAIN

The status LEDs and OLED operated normally, with no unexpected smell, noise, or heating.

## Wi-Fi Throttle

WiThrottle Lite by Beth Hoffman was selected because the free version is sufficient for initial testing. It supports one locomotive, speed and direction control, and functions F0 through F68. Its important limitation is that it cannot control track power.

The iPhone connected to the EX-CSB1 access-point network while continuing to use 5G for internet traffic. WiThrottle Lite automatically discovered and connected to the server identified as `dccex`.

The locomotive was acquired as **short DCC address 3**, its factory-default address.

## USB and EX-WebThrottle Troubleshooting

EX-WebThrottle 1.3.51 was opened in Brave, which supports the Web Serial API.

The initial apparent serial connection was incorrect. Brave offered only Bluetooth serial devices, and a Bluetooth UART entry was mistakenly selected. EX-WebThrottle showed transmitted commands such as `<=>` and `<1 A>`, but there were no received responses. This proved that the web application was not communicating with the EX-CSB1.

The original Apple USB-C-to-USB-C connection did not initially expose the expected serial device in the browser. Changing to a third-party USB-A-to-USB-C data cable and an iMac USB-A port exposed:

```text
/dev/cu.usbserial-1440
```

Selecting this device established working bidirectional communication. The key diagnostic lesson is that a displayed `Serial connected` status is insufficient by itself: a valid connection should return responses to commands such as `s` or `=`.

In Brave, pressing Return sent Direct Commands even though the on-screen **Send** button remained disabled.

## Independent Track-Power Control

The large EX-WebThrottle track-power switch is a global control. Individual TrackManager commands were used instead so output A could be controlled without energizing output B.

Commands were entered in EX-WebThrottle without angle brackets:

```text
1 A
```

This energized physical output A only.

```text
0 A
```

This switched physical output A off.

When output A was energized, the OLED reported:

```text
A: MAIN: 26 mA
```

The locomotive remained stationary at speed zero.

## Functional Test Results

With DCC address 3 selected and speed held at zero:

- F0 switched the directional headlight on.
- F8 enabled the LokSound audio.
- Current increased from approximately 26 mA to approximately 35 mA with light and sound active.
- F1 operated the bell.
- F2 operated the horn.
- F5 operated the long-horn function.
- Additional functions were accessible through the throttle.

The locomotive was then tested up to approximately speed step 10:

- Forward motion was smooth.
- Reverse motion was smooth.
- Directional lighting changed correctly with direction.
- No overload, wheel slip, unexpected noise, or erratic response was observed.

WiThrottle Lite and EX-WebThrottle both controlled the locomotive successfully. EX-WebThrottle function, direction, and speed controls did not work until locomotive address 3 was entered in its **Loco ID / DCC Address** field. The locomotive was released from WiThrottle before being acquired in EX-WebThrottle to avoid competing commands.

## Stop Versus Track Power

The WiThrottle **STOP** button sends a locomotive stop/speed-zero command; it does not remove DCC power from the rails. Consequently, sound and lighting remain active after STOP is pressed. This differs from an ESU command station whose Stop control may be configured to cut track power.

The controls have distinct purposes:

- WiThrottle STOP: stop locomotive motion while retaining DCC power and functions
- F8 off: silence/shut down locomotive sound
- F0 off: extinguish the locomotive lighting
- `0 A`: make output A and its connected rails electrically dead
- Global power-off or physical PSU disconnection: emergency or complete system power removal

## Shutdown Performed

The session ended with the following clean shutdown:

1. Locomotive speed returned to zero.
2. Command `0 A` was sent.
3. The serial connection was disconnected.
4. The USB cable was physically removed.
5. The 15 V adapter barrel plug was removed.
6. The EX-CSB1, track, and locomotive were confirmed fully de-energized.

## Outcome

The first-run commissioning milestone was successful. The following complete paths were proven:

```text
iPhone WiThrottle Lite
        |
   EX-CSB1 Wi-Fi
        |
   DCC output A
        |
Rapido/ESU LokSound 5 locomotive
```

```text
iMac + Brave + EX-WebThrottle
        |
  USB serial connection
        |
      EX-CSB1
        |
   DCC output A
        |
Rapido/ESU LokSound 5 locomotive
```

Track power, locomotive acquisition, forward and reverse motion, directional lighting, sound functions, emergency speed stop, and orderly shutdown were all verified.

## Next Milestone

Commission output B as a physically isolated programming track. Begin with read-only decoder identification and CV reads before making any CV changes. JMRI installation and infrastructure-mode Wi-Fi configuration should follow only after the basic programming-track workflow is proven.

