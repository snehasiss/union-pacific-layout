# DCC Project Context: Athearn 2-6-0 Mogul (Union Pacific #87247)

## 🚂 Locomotive Specifications & Constraints
* **Model:** Athearn 87247 HO Scale 2-6-0 Mogul Steam Locomotive (Union Pacific).
* **Chassis Architecture:** Tender-drive design with a central motor and flywheels spinning along the bottom floor of the tender, driving a drive shaft to the locomotive wheels. Low vertical space clearance.
* **Electrical Interface:** Standard 21-Pin NEM motherboard socket. Factory-installed directional LED headlights/rear lights (no upgrades needed).
* **Budget Strategy:** Replicating factory OEM-equivalent performance. Avoiding $100+ decoders to respect the locomotive's base value ($150).

## 🛒 Selected Shopping List (Trainworld Cart - Ships to India)
1. **Decoder:** SoundTraxx Econami ECO-21PNEM (Steam) [Part #881006] (~$69)
2. **Speaker:** SoundTraxx Mini Cube 3 Speaker & Baffle Kit [Part #810161] (~$13)
3. **Stay-Alive:** SoundTraxx CurrentKeeper [Part #810140] (~$29)

## 🔧 Physical Installation Plan
* **Decoder Placement:** Econami #881006 plugs straight down vertically onto the Athearn green circuit board pins in the middle of the tender cavity.
* **CurrentKeeper:** Wrapped in Kapton tape for insulation. Nests vertically in the empty rear pocket cavity behind the decoder pins, near the rear coupler.
* **Speaker:** Built using the shallowest 7mm depth profile configuration using the modular baffle rings. Glued completely airtight using plastic cement, then mounted flat against the inner ceiling of the tender coal load shell facing downward. This leaves an open air gap underneath to fully clear the spinning mechanical drive shaft.
* **Wiring Mapping:**
  * Speaker leads solder to the **SPK+** and **SPK-** pads on the Athearn motherboard.
  * CurrentKeeper Blue wire solders to **CAP+** pad on the decoder board.
  * CurrentKeeper Black/White wire solders to **CAP-** pad on the decoder board.

## ⚡ Multi-Stage Electrical Verification
* **Track Isolation:** Confirm Open Loop (no continuity/beep) between Left and Right track pickup wheels.
* **Motor Isolation:** Confirm Open Loop (no continuity/beep) between the track pickups and the metal casing of the motor frame to prevent frying the decoder.
* **Command Voltage:** Base station configured to standard 12V to 14V AC/DCC signal.

## 🚂 Decoder Core Configuration Variables (CVs)
* **CV 115 = 5** -> Changes default whistle to authentic Union Pacific Steam Whistle.
* **CV 123 = 1** -> Configures exhaust dynamics to a Light 2-Cylinder Steam layout.
* **CV 113 = 1** -> Enables Quiet Start (mute on initial layout power-up until throttle action).
* **CV 57 = 35 (Base)** -> Manually adjusted frequency to synchronize exactly 4 chuffs per single 360-degree driver wheel revolution.

## 💻 Control Architecture (Custom Web-UI Stack)
* **Command Station:** DCC-EX EX-CommandStation (EX-CSB1).
* **Hardware Interface:** Serial communications over USB-C bus (`/dev/ttyUSB0` or `COMx`).
* **Software Stack:** ReactJS Frontend web UI interacting via HTTP/WebSockets with a Python Flask backend service handling text-based DCC-EX protocol parsing.
* **DCC-EX Protocol Command Encodings:**
  * Cab Speed: `<t REGISTER CAB SPEED DIRECTION>`
  * Function Group 1 (F0-F4): `<f CAB_ADDRESS (128 + byte_value)>`
  * Function Group 2 (F5-F8): `<f CAB_ADDRESS (176 + byte_value)>`
