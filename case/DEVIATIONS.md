# Case deviations (builder, run r005)

## 1. Case = printed robot-tank v1 (release note 8)
- Contract text: base `tasks.case` asks for a new chassis, nose, wheels, levers, turret, carrier mount etc.;
  notes 3–7 refine that design.
- Change: superseded by note 8 ("Mình khỏi làm"). No new frame is drawn. v1 parts are imported from
  `case/ref/v1` as `printable: false` references; only glue-on holders are new. r003 draft files
  (build.py, covers.py, joints.py, moving.py, tools/case/*) were for the superseded design and were removed.
- Evidence: release note 8; SHA256SUMS in `case/ref/v1` and `prompts/assets/robot-tank-cadsmith-v1`.
- Cross-team: board/firmware read `case/modules.json` for module boxes.

## 2. Contract frame is left-handed; v1 map is a mirror
- Contract text: "+X phải, +Y đuôi, +Z lên"; note 8: X = −Y_v1, Y = −X_v1, Z = Z_v1.
- Finding: X × Y = −Z, so the frame is left-handed and the map has determinant −1 (mirror across the
  plane x + y = 0). Physical shape is preserved; in a right-handed viewer/slicer the model appears mirrored.
- Change: every new printed part is mirror-symmetric, so its STL prints correctly anyway. v1 refs are
  never printed from these files (reprint from the v1 originals only).
- Cross-team: a board STEP placed in this frame must use the same map; asymmetric parts need care.

## 3. Native enclosure checker does not apply
- Contract text: board 100 × 70 carrier with 4 M3 holes; `boards/main.enclosure.json` is that board.
- Finding: chassis v1 is 68 mm wide outside, hull inside 64 mm at the floor and 27 mm tall: the carrier
  cannot be mounted (note 8 says the board re-chooses its outline).
- Change: case declared handwired (`verification.nativePCBCheckerApplies: false`) and checked with
  `kicadpy.case check-print` + `case/reports/mechanical.json`. No carrier mount; free box published.
- Cross-team: board picks a smaller carrier or module-to-module wiring inside `freeBoxes`.

## 4. Connectors must be right-angle (or soldered)
- Finding: straight dupont under the ESP32 needs ≈ 30 mm; straight 6-pin plugs on the PCA9685 end headers
  hit the glacis. Holders assume 90° female plugs or soldered leads there.
- Cross-team: board/wiring docs must specify 90° plugs (or a carrier with female headers for the DevKit).

## 5. Chassis wire passages partly blocked
- Finding: the 24×24 floor window is under the PCA9685 except a 3.8 mm strip (Y −41.8…−38); the rear
  servo slots lie under the cells (already so in v1); the left mid slot is under tray A.
- Change: servo leads run along the open centre lane under the chassis and up through the right mid slot
  or the window strip. Flat 3-wire lead 3.6 mm passes; the 7.5 × 2.5 plug passes edge-on (8 × 5 slot,
  3.8 mm strip) – thread the leads before fitting the PCA.
- Cross-team: none (wiring order goes into the assembly guide).

## 6. Release note 9: v5 stack_base replaced on the car by stack_bridge (plate + 4 legs)
- Contract text (note 9): import stack_base / tiers / turret mount; check whether the stack_base M3 82×20 pitch matches
  printed holes; if not, propose a printed adapter that screws or clamps on, without drilling.
- Finding: no printed hole matches 82×20 (hull screws 60×56, LED bracket 24). The 92 mm base does not fit inside the
  hull, and tiers in front of the cells would hit the glacis.
- Change: the new glue-on `stack_bridge_plate` (same 4 pegs as stack_base) sits on 4 `stack_leg_*` glued to the
  chassis floor beside the cells, following our glue-on holder rule rather than screws. v5 parts are imported unchanged.
  `stack_base` stays in parts.json as DO NOT PRINT for the car.
- Cross-team: tier positions on the car are in `case/modules.json` → `layoutB`.

## 7. Two exclusive layouts in one parts.json
- Option A (lid on, in-hull holders) is assembled on the car. Option B (lid off, stack) is drawn shifted +130 mm in X,
  so the two layouts never overlap in the file.
- `tools/case/fit_checks.py` moves group B back onto the car (`B_SHIFT`) and checks it against the car parts that B
  keeps: hull, chassis, wheels, arms, servos, cells, cradle and trays. Layout-B wire routes are in `case/layout_b.json`
  (on-car coordinates), not in interfaces.json. The harness wire check would test them against the shifted drawing,
  which would be meaningless. The turret-on-stack joint is in interfaces.json at the shifted position, where it is valid.

## 8. Integration: the board's 62×60 carrier is kept; layout B is the buildable layout
- Text: release note 9 (stack, separate modules default) and the lead review. The board kept its 62×60 carrier
  (engineering/DEVIATIONS.md items 7 and 10). It is the only place for the servo power switch (ACT_EN), the OE
  pull-up, the U1 buffer and the Echo level shifters.
- Finding: in layout A (lid on), the carrier volume (contract X ±31, Y −46…+14, Z 49…~68) is exactly where the
  ESP32 posts, PCA9685 posts and charger trays sit. The hull is 27 mm tall, so the carrier cannot fit alongside
  the DevKit, PCA9685 and chargers. Layout A therefore stays only as the record of the printed‑hull fit. Its
  wiring is withdrawn from interfaces.json, and its frozen parts are unchanged.
- Change (layout B): new `stack_carrier_deck` between `stack_bridge_plate` and the PCA tier.
  - Underside: 5.0 sockets with 45° roofs that sit on the bridge pegs.
  - Carrier mounting: 4 M3 posts at H1…H4 (M3×8 self‑tap). Carrier board corner at (−31, 12.5), underside Z 77.9.
  - Columns: 4 columns beside the carrier carry the v5 pegs to Z 109.5. That gives 30 mm over the board top for
    vertical servo plugs, meeting the board's ≥ 13 mm spacer request in one part.
  - Tiers: the 3 imported v5 tiers move up 43.1 mm with their geometry unchanged (`rework` in checks.json).
  - Wiring: all leads end at the carrier connectors J_S0…6, J_SONAR_F/R, J_CTRL, J_PCA and J_PWR (case/layout_b.json).
  - Coupon: `coupon_deck_TEST_ONLY` covers the deck fits.
- Evidence: fit_checks `layoutB:*` all pass on the car (hull, cells, cradle, trays, bridge, servos), and every
  layout‑B wire has 2 open routes.
- Cross‑team: the board reads the tier boxes in case/modules.json → layoutB.
  - The turret on the stack now tops out at Z 214.8 (estimated CG Z ≈ 65 mm, side tip ≈ 35°).
  - Fan (tester finding): the 30×30 5 V fan is zip‑tied under `stack_tier_1` through the tier's own 4 zip
    slots, so no new part is needed. It sits at X ±15, Y 27.5…57.5, Z 99.5…109.5, blows down on the carrier
    (4 mm above C1) and draws air through the tier window. Its ~60 mm lead to J_FAN has 2 checked routes. The
    sonar and J_PWR leads that crossed that spot are re‑routed (all open). The lid `fan_plate` remains layout A only.
  - Firmware: case/firmware-limits.json gives yaw −70…+70 (both turret options, checked on STEP; the wire slack
    loop is not simulated).

## 9. Integration review 2: layout B holds the board's DECIDED two-island power chain
- Text: lead finding on case/layout_b.json. Board deviation 8 / engineering/POWER_SYSTEM.md "Release note 8 — DECIDED":
  protected 1S pack (PCB-Li-1S15A + F_PACK 0287015.U in FH_PACK 0FHA0002XP) → XT60-class RUN plug → two Pololu U3V70F5
  with inputs in parallel and outputs never joined; A → J_PWR, B → 5 A fuse → red wires of CH3–5; ACT_EN → B ENABLE.
- Change (new parts only, case/power_b.py; no closed part edited):
  - `protector_holder`: wall + end lips in front of the cell ends, 4 mm bus gap, PCB top under the bridge plate (Z 63.0 vs 63.4).
  - `fuse_holder_pack`: FH_PACK on edge right in front of the cells. `conv_holder_a/b`: each U3V70F5 on edge, ends open for leads.
  - `fuse_clip_b`: the 5 A inline holder on the 45° right side wall (flat glue face on the slope, prints glue face down).
  - `coupon_power_TEST_ONLY`: one end of each, with its real slot/lips and glue face.
  - The layout-A trays `power_tray_a/b` (user's "5V 2A" modules) are NOT fitted in layout B; the front floor bay is theirs.
  - Wiring (layout_b.json + interfaces.json, 2 routes each): cell bus → F_PACK → protector → XT60 → A/B VIN Y-harness (14 AWG,
    6.2 mm pair), A VOUT → J_PWR, B VOUT → F_ISLAND_B → CH3–5 red-wire splice beside the carrier right edge, J_CTRL.6 ACT_EN →
    B ENABLE. The servo-lead risers through the mid slot and the front window now go straight up first (still 2 open routes each).
- Not met / open:
  - M_CHARGE (Adafruit 6091): no room in the printed hull without blocking a servo riser. It stays OFF the car (bench): unplug the
    RUN XT60 (parked on the floor, right front corner) and lift the pack plug out (16 mm route) to the charger. Matches the board's
    "RUN and CHARGE mutually exclusive plugs; no running while charging".
  - Unfused lead (integration review 3, chosen): the case cannot hold the 0FHA0002XP within 25 mm of the cell bus
    without blocking a servo-lead riser (measured bay, build/case/probe_floor.py). So F_PACK stays INSIDE the sealed
    pack, fitted by the pack maker per POWER_SYSTEM.md (<=25 mm unfused there). `fuse_holder_pack` then only parks
    and strain-relieves the pack's fused lead / holder body; the case route 'cell bus + -> F_PACK holder' is that
    pigtail. Board team: please confirm in engineering/DEVIATIONS.md (board domain, not edited by case).
  - Charging bench-only (M_CHARGE off the car, RUN XT60 unplugged first) is the case choice; board team: please
    record it in engineering/DEVIATIONS.md so all teams follow the same rule (RUN and CHARGE mutually exclusive).
  - Every power-device size is GIẢ ĐỊNH (U3V70F5 40.6×15.2×4.6 from the lead/board; FH 39×22×12, protector ≤45×20×4.5,
    5 A holder 32×14×10 not from a drawing). Print the coupon first.
- Evidence (re-run on the final case/out/parts.json, hashes recorded in both reports): tools/case/fit_checks.py pass, 151 checks; kicadpy.case check-print pass (holders and devices clear on the car, all 22 layout-B wires ≥ 2 open routes).
- Cross-team: firmware/WIRING.md must describe this chain (lead finding 2, firmware domain, not edited here).
  Board: case/modules.json layoutB lists M_SERVO_BOOST(_B), FH_PACK, M_PROTECT, F_ISLAND_B boxes.

## 10. Integration review 3: battery-fed 5 V logic branch for the ESP32 DevKit (layout B)
- Text: lead finding on case/layout_b.json: "layout B has no holder, position or wire route for the DevKit's battery-fed
  logic 5 V supply … Add a glue-on holder for the logic converter (U3V16F5 ≈8.1×13.2×2.5 mm or the chosen module) … and a
  checked route from the RUN harness to it and from it to the DevKit USB end on tier 2, without blocking existing risers."
- Change (new parts only, case/logic_b.py; no closed part edited): `logic_holder` — flat floor tray (15.2×10.9×4.5) for an
  M_LOGIC Pololu U3V16F5, glued with 502 on the solid hull floor left of the front window (v1 x 47..62, y 17..28; contract
  X −27.9..−17, Y −62.2..−47). Ends open for the leads, foam tape under the module. `ref_logic_B` envelope;
  `coupon_logic_TEST_ONLY` = the holder itself. Risers (0,−8.3)/(39.9,0) and every earlier route stay open.
- Wiring (2 routes each, checked): XT60 RUN Y harness third branch → U3V16F5 VIN/GND (22 AWG, 3.0 mm); VOUT/GND → USB
  power-only lead up the open nose, outside the stack, into the DevKit USB port at the stack front (same exit as the host
  cable; the stack's ESP32 tier is called "tier 3" in the route names, it is the lead's "tier 2" above the PCA tier).
- Case choice (board to confirm): the lead is a USB power-only pigtail soldered to VOUT/GND ending in the plug the real
  DevKit takes (micro-B on most 30-pin DevKits, GIẢ ĐỊNH; the old chain text says USB-A socket + A-to-C cable, written for
  the LILYGO). A USB-A socket + cable joint would need a ~16×8 mm plug body in the bay; the pigtail needs only the 4 mm route.
  Same rule as the board: portable = this lead plugged, host = unplug it and plug the host data cable; never both, no Y cable.
- Not verified: U3V16F5 size/pin ends, its draw in the pack budget (board), the real DevKit connector type.
- Evidence: tools/case/fit_checks.py pass, 161 checks (holder print, collisions on the car, both new wires 2/2 open routes).
- Cross-team: board must publish M_LOGIC in the DECIDED chain + parts.json externalParts purpose (DevKit, not LILYGO);
  firmware/WIRING.md must name it (lead findings 1 and 3, other domains, not edited here). modules.json layoutB: M_LOGIC box.
