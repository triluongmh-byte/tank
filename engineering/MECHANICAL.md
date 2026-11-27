# Board integration with the printed robot-tank v1 case (release note 8)

Status: DESK FIT ONLY from the hash-checked v1 sources (prompts/assets/robot-tank-cadsmith-v1: model.py, report.json). Nothing was physically test-fitted; the case team must confirm with the real STEP set and printed parts.

## Carrier box published for case/firmware
- Outline 62 x 60 x 1.6 mm (X x Y x Z), 2 layers, all parts on top, tails <= 4 mm below. Corners square, copper edge clearance 0.5 mm.
- Case frame (+X right, +Y tail, nose -Y, +Z up, origin on ground at vehicle centre): board corner (front-left) at X=-31, Y=-46; underside plane Z=49 (top of the v1 hull bosses at z=43+6). Board X = x-31, Y = y-46. In the v1 model frame x_v1 = 46-y, y_v1 = 31-x.
- Body envelope X -31..31, Y -46..14, Z 49..~68 (tallest part: C1 1000 uF 10 mm dia x 16 mm at board (16.5,35) -> case X -14.5, Y -11). Mating plugs on the headers add height: the cavity ceiling (lid underside) is Z=70 and the lid has four 4 mm Nano standoff posts down to Z=66 at v1 x=-7.6/35.6, y=11.4/26.6 (case X -26.6/-11.4, Y -35.6/+7.6). Posts and plugs are NOT verified to clear each other.
- Mount holes (3.2 mm, copper keep-out R3.6): H1 (3,26) H2 (59,26) H3 (59,52) H4 (3,52) -> case (X,Y) = (-28,-20) (+28,-20) (+28,+6) (-28,+6). The Y=-20 pair sits on the existing hull bosses (v1 x=20, y=+-28, M3 clearance holes already in the chassis plate). The Y=+6 pair (v1 x=-6) has NO printed boss: propose two printed rails 8 x 34 x 6 mm lying on the chassis plate at y_v1=+-28 from x_v1=20 to x_v1=-6, bolted through the existing boss holes, each with an M3 nut trap at x_v1=-6. Plate/3MF only for these added parts; no print job sent.

## Why the earlier carrier does not fit
v1 chassis is 68 mm wide outside; the hull cavity is +-32 mm (64 mm) up to z=48.8 and widens at 45 deg above. The 100x70 carrier and its 4 mm-in mount pattern cannot fit. The 4 unused Nano posts (v1 x=-40/20, y=+-28) cannot take the board because the two 18650 cells occupy x_v1 -77..-12, |y|<19, z 43..61.6 below that span, and the carrier is 60 mm long. The carrier therefore occupies x_v1 -14..46 only and is cantilevered 26 mm toward the nose beyond the Y=-20 hole row.

## Keep-out and clearance rules for the case
- Turret SG90 sits in the lid at v1 (0,0) (case X 0, Y 0 = board (31,46)) and its body hangs below the lid; its bottom is estimated at about Z=57 from the nominal 22.5 x 12.1 x 23.4 servo. Parts near board x 15..47, y 30..60 must stay below Z~56 until the real servo cutout depth is measured. Tall parts in that area: J_FAN pins 45.5-50.6 (x) at y=52 are the only 10 mm class parts there (terminal at x 42..56); C1 and J_PWR are outside it (x < 24).
- Screen ribbon: the v1 glacis window and the 24 x 24 chassis opening at v1 x=50 are ahead of the board (board front edge is v1 x=46). Cable room 4 mm only.
- Hull side windows/rear 16 mm window are not used by the carrier. J_PWR (board (10,48)) and J_FAN (45.5,52) wire-entry side per the Phoenix 1715721 drawing (not verified here); check that the DevKit/PCA9685/modules leave 12 mm for screw drivers. The ESP32 DevKit, PCA9685 module, four charge/boost modules and the 30x30 fan do not yet have mounts in v1 (see the case report); only the carrier and its two rails are proposed here.

## Files
board-geometry.json and native-pads.json are measured from the actual PCB; build/board/main-contract.step (see step-handoff.json) is the populated STEP in the sealed board frame (origin at board corner, Z 0..1.6): translate it to case X=-31, Y=-46, Z=49 and apply NO second Y mirror. Wire/pin positions: pinout.md.
Both external power modules and the pack stay off-carrier (POWER_SYSTEM.md); do not infer their size from this file.

## Release note 9 addendum
Two mounting configurations now exist for the unchanged 62x60 carrier: (A) lid ON, carrier on hull bosses + rails at Z=49 as above (turret on lid, option (a)); (B) lid OFF, stack on the chassis with the carrier on an ADDED deck tier (T1). The carrier cannot be dropped and does not fit a 74x43 tier; see STACK_WIRING.md for the reasoning, tier boxes and wire runs. The lid keep-outs above (turret servo depth, Z=66 posts) apply to (A) only; for (B) the keep-outs are the tier pitch 26 mm (carrier parts <= ~17 mm above the board, 10 mm bulk cap C1 16 mm fits), the 8.5 mm overhang each side and servo-plug room.
