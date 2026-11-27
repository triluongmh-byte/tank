# Stack wiring and module placement (release note 9, cadsmith robot-tank v5)

Status: DESK ESTIMATE from hash-checked v5 sources (prompts/assets/robot-tank-cadsmith-v5/model.py, report.json). Nothing measured or fitted. PCA9685 62.2x25.4 and DevKit 51.5x28.3 are cadsmith ASSUMPTIONS; measure the real modules first. No print or job sent.

## Where the safety circuits live (decision)
Q1/Q2/Q3 + ACT_EN switch (servo power default OFF), R5 PCA_OE_N pull-up, U1 PWM isolation buffer, U3-U6 HC-SR04P TRIG/ECHO level translation, F1, J_FAN exist ONLY on the 62x60 carrier (design/main.kicad_pcb). Loose PCA9685 + DevKit cannot replace them, so dropping the carrier is NOT allowed: servo power would be un-gated and Echo (supply-level) would hit 3.3 V GPIO. The carrier is kept unchanged (pin table, rails, 0x40 CH0-5 wheels / CH6 turret, OE, ACT_EN, Echo shifting, separate servo/logic branches).
The carrier does NOT fit a 74x43 tier (60 mm > 43 mm; its 56x26 M3 holes vs the tier's 55.9x19.05 M2.5 pattern: the 56 mm axis matches, the 26 vs 19.05 axis does not). Re-laying it into 43 mm was judged infeasible (7 servo headers + two 2x6 hubs + 10 mm bulk cap + 2 terminal blocks need ~3700 mm2; a tier offers ~2900 mm2 minus the 46x26 window). Chosen V0 option: carrier on an ADDED printed "carrier deck" tier (case team to draw; adapter only, no change to printed parts): 74-long plate on the same pegs/sockets, carrier long side (board x, 62) along stack X, board y (60) across stack Y overhanging the 43 mm tier by ~8.5 mm each side (hull cavity is 64 mm wide; check clearance), four M3 posts at the carrier holes. Add 26 mm to stack height.

## Tier order (stack frame, origin = stack footprint centre, Z up from stack_base bottom; base_t=3, tier pitch 26, board standoff 7.5)
| Level | Z bottom | Content | Box (X x Y x Z mm) |
|---|---|---|---|
| base | 0 | stack_base 92x43x3, M3 82x20 | needs adapter to chassis (see below) |
| T1 | 3 | carrier deck (ADDED) + carrier 62x60x1.6, parts to ~17 mm above board | 62x60 on 74x62 deck; board bottom Z=10.5, top parts to ~Z28 |
| T2 | 29 | PCA9685 on 4 M2.5 posts 55.9x19.05, board bottom Z=36.5 | 62.2x25.4x10.1 (+8.5 headers) |
| T3 | 55 | ESP32 DevKit on 2 rails, board bottom Z=62.5 | 51.5x28.3x12.8 |
| cap | 81 | stack_turret_mount (option b) top Z=89; SG90 above to ~119 | 109.4x43x35.4 |
Without the carrier tier (note-9 literal default PCA=T1, ESP=T2) the numbers are cadsmith's: PCA Z10.5, ESP Z36.5, cap Z55..63, turret top ~Z97. Carrier tier shifts everything above by 26 mm. Stack stands on the chassis top (Z=43 in the v1 frame) when the lid is off, so add 43 for absolute height. Centre of gravity moves up/forward with the stack; case to compute.

## Wire lengths (cut length incl. ~30 mm service slack; Dupont/JST, measure after fit)
- J_CTRL (12-way, carrier T1) <-> DevKit T3 (GND,3V3,GPIO21/22/25/26/32/34/33/35,GND,GPIO27 STOP_N): 2 tiers = 52 mm vertical + ~50 mm run -> 110-130 mm.
- J_PCA (12-way, carrier T1) <-> PCA9685 T2 header (3V3,GND,SDA,SCL,OE,6 PWM): 26 mm vertical + 40 mm -> 90-110 mm. If the PCA is also wired SDA/SCL to the DevKit those share the J_CTRL lines on the carrier; do not add a second parallel I2C run.
- 7 servos: plugs go to carrier J_S0..J_S6 (T1, lowest tier = shortest). Servo axes are ~60 mm below the chassis top and up to 52 mm fore/aft, 35 mm to the side of the stack centre: ~150-190 mm of lead; a stock SG90 lead is ~250 mm (measure); a 200 mm extension fits all. Lead slots: the 4 zip slots per tier at (12,18) mm.
- Sonars: option (a) 4-wire x2 to turret head J_SONAR_F/R, option (b) the same from the stack cap: both 150-250 mm; use 4-core 28 AWG.
- Power: J_PWR from the boost module output 150 mm 18 AWG (6 A budget, see POWER_SYSTEM.md). J_FAN 2-wire 22 AWG to the fan, 200 mm.
- Display (8 wires: 3V3,GND,SCK GPIO18,MOSI GPIO23,CS GPIO16,DC GPIO17,RST GPIO4,BL GPIO13): from DevKit T3 header.
## Option (a): turret on lid, screen behind the v1 glacis
Needs the lid ON, so the stack cannot stand on the chassis (hull is 27 mm tall, a tier 26 pitch + base does not fit). Modules go inside the hull as in release note 8 (carrier on bosses/rails, MECHANICAL.md) or the stack stands beside the car on long leads (v5 model: stack_xy 0,-112). Screen leads DevKit -> glacis window ~120-160 mm; turret SG90 3 wires + sonar 8 wires ~200 mm via the lid wire hole.
## Option (b): turret and screen on stack_turret_mount (lid off, stack on chassis)
Screen: face panel 45 deg at front of cap, DevKit T3 -> panel ~60-80 mm (use 100 mm). Turret SG90 sits on the cap: carrier J_S6 (T1) -> turret ~120 mm + 52 mm drop = 170 mm; sonar wires go up the posts, 150-200 mm. Turret top ~Z140-166 above ground; keep wires on the 4 posts with zip slots so the cap can rotate nothing (the servo, not the cap, rotates).
## Extra tier for a power module
Add one more identical tier ("P") above/below T3; the 1S charge+boost "5V 2A Type-C" module (size NOT measured) takes the 46x26 window area or a zip-tied slot (4 slots, 4x2 mm). Put the module at the tier's side edge so the Type-C port faces outward (USB path needs ~10 mm). Its 5 V output goes only to J_PWR; the DevKit USB (host link) is a separate port reached from a tier edge. Cell connection/protection unverified; boost outputs never paralleled.
## Stack_base vs printed chassis (board's reading for the case team)
Base M3 pattern 82x20 matches none of the printed chassis holes (bosses 60x56 at v1 x=-40/20, y=+-28; bumper holes (68,+-12); 24 mm window at x=50): case must provide an adapter bolted through existing holes; nothing is drilled.

## Servo-plug clearance under T2 (tester finding, configuration B)
J_S0..J_S6 are vertical 1x03 headers; board top is ~Z12.1 and the T2 tier floor is Z=29 (17 mm). A mated 3-pin servo plug is ~11 mm above the board top (2.5 plastic + ~8.5 housing) and the lead must bend ~10 mm radius before it can leave sideways, so 17 mm is NOT enough for vertical exit. Required for the carrier-deck tier: raise the T2 floor by >= 13 mm (carrier-deck-to-T2 pitch >= 39 mm instead of 26; a 13 mm printed spacer ring on the pegs) giving ~30 mm, or use right-angle headers (not done; it would change the footprints and the checked board). Headers at stack coordinates (-27,-16),(+27,-16),(-27,+7),(+27,+2) lie under the T2 plate, so the spacer is needed. This adds 13 mm to every Z above T1 in the table (turret top ~Z153-179 above ground). Unverified.
## Allowed footprint along the car (configuration B)
In the v1 frame the cells occupy x -77..-12, |y|<19, z 43..61.6, hull bosses at y=+-28 reach Z=49, glacis starts near x=56 at the top. Keep the 92 mm base and the 62 mm deck inside x_v1 -12..+82 (stack centre x_v1 >= 34, i.e. case Y <= -34), centred on y_v1=0 (the 43 mm base clears the y=+-28 bosses; the deck underside is >= Z53 so its 8.5 mm overhang passes over them). Front end vs the hull glacis wall must be checked by the case team.
