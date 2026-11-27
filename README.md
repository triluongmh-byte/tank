# Pet Tank 🛞🤖

**English** · [Tiếng Việt](README.vi.md)

A 6-wheel armored-car-style tank cloned from **claude-pet**. A screen on the sloped front face shows the pet face and the status of Claude Code sessions. A turret carries two sonars mounted back to back for finding a path.

- **Body:** the `robot-tank` v1 case designed in cadsmith, already printed by the owner, plus the v5 board stack and glue-on/clip-on holders.
- **Board:** 62×60 mm two-layer carrier.
- **Control:** ESP32 DevKit + PCA9685 driving 7 servos: six 360° wheel servos and one SG90 turret servo.
- **Power:** two 18650 cells in parallel (1S) through a pack protector and two 5 V boost modules.

> **Status:** the design passed the team's board, firmware, case and integration checks. **Hardware is untested.** The firmware has not been flashed, the new holders have not been printed, and no board has been ordered. Module dimensions in the docs are **ASSUMPTIONS**: measure the real modules before printing or soldering.

## What's in the repo

| Folder | Contents |
|---|---|
| `design/` | KiCad project: schematic, PCB, libraries, component 3D models |
| `engineering/` | Power ([POWER_SYSTEM.md](engineering/POWER_SYSTEM.md)), stack wiring ([STACK_WIRING.md](engineering/STACK_WIRING.md)), assembly, bring-up, pinout, calculations |
| `parts.json`, `product.json`, `manufacturing.json` | BOM (LCSC part numbers), board description, fabrication settings |
| `case/` | CadQuery scripts for the holders ([build.py](case/build.py), `holders.py`, `stack.py`, `power_b.py`, `logic_b.py`). `case/ref/v1` and `case/ref/v5` hold the original STEP files of the printed robot-tank, unchanged |
| `firmware/` | ESP32 firmware (`firmware/tank/`), [wiring guide](firmware/WIRING.md), [host protocol](firmware/PROTOCOL.md), host-side tests (`firmware/tests/`), host bridge (`firmware/host/`) |
| `tools/` | Check and export scripts for each team (board, case, firmware) |
| `contract/` | The sealed team contract and release notes (the owner's words verbatim, plus how the lead interpreted them) |
| `prompts/`, `references/` | Original request, request history, reference images. STEP/STL files under `prompts/assets` are not committed; their hashes are in the `SHA256SUMS` files |

Not committed, because `./build.sh` regenerates them: STL/STEP/3MF, Gerbers, zips, renders, `build/`, `boards/`, `case/out/`, `case/print/`, firmware binaries. Datasheets are not committed either; their links are in `engineering/sources/manifest.json`.

Most docs inside the subfolders are written in Vietnamese.

## Build

```sh
./build.sh              # board -> case -> firmware
./build.sh firmware     # a single stage
./build.sh board case
```

Requirements (nothing is installed from the network):

- `KICAD_HARNESS_PYTHON` (Python with `kicadpy`) and `KICAD_CASE_PYTHON` (Python with CadQuery + `kicadpy`). Harness provides both.
- KiCad 9 `kicad-cli`. The script looks in `/Applications/KiCad/KiCad.app`, or set `KICAD_CLI`.
- Bambu Studio at `/Applications/BambuStudio.app`, used to slice `case/print/*.3mf`. No print job is ever sent.
- `arduino-cli` with core `esp32:esp32@2.0.14` already installed. If the core is outside the default location, point `ARDUINO_DIRECTORIES_DATA` at it (Harness keeps it in `~/.cache/autonomous-circuit/firmware/arduino`).

A build rewrites a few committed files: the board STEP hashes in `case/ref/board/SHA256SUMS`, `engineering/step-handoff.json` and `case/firmware-limits.json`. Seeing them change after a build is expected.

What each stage does:

- **board:** runs the official board checks (ERC/DRC, netlist, gate) and writes the manufacturing packet to `boards/`. Exports the populated board STEP to `build/board/main-contract.step` and hands it to the case (`case/ref/board/`, hashes recomputed).
- **case:** runs `case/build.py`, which writes STEP/STL to `case/out/`. Then runs the three case checks: printability and collisions, v5 against v1, and turret sweep. Then generates the print plates `case/print/production.3mf` + `test-only.3mf` and `case/overview.html`, and runs `kicadpy.case check-print` (printable surfaces, bed fit).
- **firmware:** runs the host tests, including mocks and ASan/UBSan, then compiles the ESP32 build to `build/firmware/esp32/tank.ino.bin`. **Nothing is flashed.**

When a requested stage reads another stage's output and that output is missing, `build.sh` runs that stage too. The case needs the board STEP. The firmware needs `case/reports/turret_yaw.json` for the turret limits.

## What the firmware does

- Keeps claude-pet's pet face and Claude Code session status, now on a 1.54" 240×240 ST7789 screen.
- Talks to a computer over USB (UART0, 115200).
- **Phone control**, modelled on the UI of the owner's crab-robot-v17g:
  - The tank starts its own open Wi-Fi network named `XeTang-XXXX`. The screen shows the network name, the address and a QR code.
  - Join that network and open `http://192.168.4.1/`. Many phones open the page on their own.
  - **Drive** page: an 8-direction pad. Hold a button to drive, release to stop. Three speeds: 0.4 / 0.65 / 1. Forward or reverse is blocked when the sonar facing that way sees an obstacle closer than 350 mm, or has no fresh reading (older than 250 ms). The light button shows "not connected" because the lights have no control pin yet.
  - **Assembly** page: set the centre, limits and direction for each wheel, centre the turret (limited to ±70°), then Save. Driving is refused until calibration is done.
  - **Wi-Fi** page (optional): join a home network. The password is stored in NVS.
  - Every stop source wins: releasing the button, no command for 500 ms, losing the phone connection, the STOP button, an I2C error, the watchdog.
  - The constants (500 ms, 5 s, 60 % pulse at speed 1) are **untested** on the real tank and a real phone.
- The board adds a logic boost module, `M_LOGIC` (Pololu U3V16F5), that powers the DevKit over USB from the battery. The tank can run without a computer attached.
- Drives the six wheels (PCA CH0–5) with per-wheel calibration, and the turret (CH6).
- A stop-and-go path-finding mode using the two HC-SR04P sonars. `AUTO SCAN` stays locked until the real turret angles are measured on the tank.
- Always boots stopped. Losing the link, a missed heartbeat, or the STOP button (GPIO27) cuts servo power.

GPIO map: see [firmware/README.md](firmware/README.md) and [engineering/esp32-pinmap.json](engineering/esp32-pinmap.json).

## Case: what to print and how to assemble

See [case/README.md](case/README.md). In short:

- **Do not reprint** the robot-tank v1 parts that are already printed: chassis, hull, lid, turret, light bracket, six arms, six wheels.
- Print the new glue-on/clip-on holders and the **v5 stack**: base, PCA9685 + fan tier, ESP32 tier, and a cap with a turret-servo pocket and a 45° face for the screen.
- **Layout B** is the chosen layout: the lid is removed and the stack stands on a bridge plate above the two cells. Total height is **214.8 mm**, against 118.3 mm for v1. Only layout B fits the 62×60 carrier with all the modules.
- Print the **TEST ONLY** plate first and try it with the real modules before printing the production plates.

## Things you may need to fix by hand

The testers recorded the points below. Items 1–8 come from run `r006` and may be partly fixed. Items 9–11 come from the latest run, `r007`. Neither run produced a `lead-document-findings.json`. None of these have been measured on hardware.

1. **The servo boost converters are near their limit.** The estimated peak current drawn from the battery is ~8.9 A, above the 8 A typical rating of the Pololu U3V70F5. Measure the real current with all six wheels stalled or starting, and consider limiting speed or splitting the load.
2. **The power docs still contain old text.** Some lines in `product.json`, `engineering/POWER_SYSTEM.md` and `parts.json` still describe the old power chain (TPS61287, LILYGO, 100×70 carrier, 12 AWG / 30 A wiring). The current design uses two Pololu U3V70F5 modules, an ESP32 DevKit and a 62×60 carrier. The main battery lead needs connectors rated ≥15 A to match the `F_PACK` fuse.
3. **ACT_EN while the ESP32 boots.** The second boost module's ENABLE pin is tied to ACT_EN through a Dupont lead and pulled up to VIN (≤4.2 V) through 100 kΩ. Check on the bench that ACT_EN stays low while the ESP32 boots and resets, so the servos don't twitch.
4. **The 2×6 header orientation in `firmware/WIRING.md`** does not match the new 62×60 layout. Use [engineering/pinout.md](engineering/pinout.md) when crimping the `J_CTRL` / `J_PCA` leads.
5. **The unfused battery lead is ~35 mm long**, over the ≤25 mm limit. Move the `fuse_holder_pack` holder closer to the cells, or fit `F_PACK` inside the battery pack.
6. **There is no place for the charger on the tank.** To charge, unplug the RUN connector and charge on the bench.
7. **Module dimensions are assumed:** ESP32 51.5×28.3, PCA9685 62.2×25.4, fan 30×30×10, screen 32×38×4 mm. Measure the real parts and print the TEST ONLY coupons first.
8. **Layout B makes the tank almost twice as tall** and drops the lid. Keeping the v1 lid needs a redesign by the team.
9. **The power diagrams don't show `M_LOGIC` yet.** Parts of `engineering/POWER_SYSTEM.md` still say the DevKit takes 5 V from its own USB supply, and one line still mentions the LILYGO. `case/logic_b.py` and the firmware integration report still refer to the old "optional chain". The bring-up order in `firmware/WIRING.md` (logic first, then islands A/B) does not match the diagram, where all three boost modules are wired in parallel at the RUN lead.
10. **Where the DevKit sits:** the `M_LOGIC` wire route says the DevKit is on "tier 3", while `STACK_WIRING.md` and `parts.json` put it on tier 2. Tier 2 is correct.
11. **Power the DevKit through its USB port only.** Do not also feed its VIN pin in parallel with USB.

## Safety

A 1S Li-ion pack delivers high current. Fit the protector and fuses described in [engineering/POWER_SYSTEM.md](engineering/POWER_SYSTEM.md). Never connect the outputs of the two boost modules in parallel. Never power the servos from the DevKit's 5V pin or from a computer's USB port.
