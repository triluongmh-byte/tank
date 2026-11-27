# 1S battery power assembly — release notes 1–2, V0.3 pack-fault repair

> **PRIMARY design = the last section, "Release note 8 — DECIDED" (two Pololu U3V70F5 islands).** Everything from here to that section (TPS61287EVM chain, 12 AWG/30 A, fault table, LILYGO wording, 100×70 mm carrier) is the OPTIONAL reference chain, kept for history; the carrier is 62×60 mm and the MCU is an ESP32 DevKit (USB host/logic branch), not a LILYGO.

```text
PRIMARY (two islands, outputs never joined):
 protected 1S pack (PCB-Li-1S15A) --F_PACK 15 A--+--> U3V70F5 #1 --> J_PWR -> F1 -> Q1 -> LOAD_5V -> Q2/Q3 (ACT_EN) -> SERVO_5V
                                                  |        (A: CH0-2, turret CH6, fan, sonar; 3.56 A)
                                                  +--> U3V70F5 #2 --5 A fuse--> red wires of servos CH3-5 (B; 2.4 A)
                                                           ENABLE <-- ACT_EN tap, 4.7 k to GND (off by default)
 ESP32 DevKit: own USB 5 V branch; GND common at pack negative / J_PWR.2
```

This is the selected **external power assembly**, connected to the existing carrier. It is a desk-verified reference design, not a tested supply or evidence that the owned 140 g pack meets it. `parts.json.externalParts` lists the actual modules and `externalModificationParts` their replacement components; `power-calculations.json` contains reproducible estimates. Do not connect 1S directly to J_PWR. Keep the carrier (now 62×60 mm after note 8), mounts, GPIOs and servo reset circuit unchanged.

## Connections and operating modes

```text
sealed 1S parallel-18650 pack, qualified >=15 A continuous, 4.20 V charge
    [inside sealed assembly: F_PACK 0287015.U / FH_PACK 0FHA0002XP
     at B+ takeoff, plus PCB-Li-1S15A; see placement below]
    P+/P- protected two-wire outlet
        |
        +-- keyed RUN plug (unplug this whole branch to charge)
        |      M_PACK_BREAKER J1/J3 input, J2/J5 output, 12.8–14.8 A latch-off
        |      +-- 12 AWG short pair --> M_BOOST J1 VIN+ / J2 VIN-
        |      |      TPS61287EVM-042, MODIFIED to 5.13 V (stock is 18 V!)
        |      |      J3 VOUT+ / J4 VOUT- --> M_BREAKER J1 VIN / J3 PGND
        |      |      TPS259824OEVM, modified and configured as below
        |      |      J2 VOUT / J5 PGND --> 18 AWG --> J_PWR.1 EXT_5V_IN / .2 GND
        |      |         carrier F1 -> Q1 -> LOAD_5V -> J_FAN.1 +5V
        |      |                            GND     -> J_FAN.2 GND
        |      |                            Q2 -> SERVO_5V (default OFF)
        |      +-- M_LOGIC U3V16F5 VIN/GND --> VOUT/GND --> USB-A power socket
        |             --> ordinary USB-A to C cable --> ESP32 DevKit USB (was LILYGO USB-C before release note 8)
        |
        +-- ALTERNATIVE CHARGE plug --> M_CHARGE BATT+ / BATT-
               Adafruit 6091 bq25185 USB-C charger, 4.2 V Li-ion, 1 A
               CHARGE LOAD output stays empty. USB-C input from 5 V/2 A adapter.
```

RUN and CHARGE use **one pack outlet and mutually exclusive mating plugs**, not a Y cable. No running while charging. A qualified pack assembler supplies the sealed protected pack/fuse and verifies its cells, interconnects, NTC, chemistry and charge rating; this project does not instruct the owner to open, weld or modify bare cells. The selected protector is AA Portable Power/BatterySpace PCB-Li-1S15A (#2069), 15 A continuous, ≤20 mΩ path, common P+/P- charge/discharge; its published overcurrent trip is **65±10 A**, not 15 A. F_PACK and the separate M_PACK_BREAKER below are mandatory; the protector's name is not a current limiter. Overcharge backup 4.25±0.05 V; overdischarge backup 2.5±0.1 V. The precision charger and earlier motor UVLO are the normal operating limits. No 2-cell count is inferred from 140 g.

Portable mode uses M_LOGIC USB power. Host mode physically replaces that cable with the host USB data cable, leaving M_LOGIC's output disconnected. LILYGO has one USB-C receptacle. No USB Y cable, joined USB positives or carrier-to-LILYGO 5 V wire. This retains USB CDC and prevents battery/host backfeed without changing firmware. The two boost **outputs are never connected together**; their inputs share the protected pack and grounds share P-. LOGIC_3V3 still comes only from LILYGO.


## Selected pack fuse and coordination — tester finding 1

**F_PACK = Littelfuse 0287015.U, 15 A ATOF, 32 VDC, 1000 A DC interrupt**, in **FH_PACK = Littelfuse 0FHA0002XP, 30 A / 32 VDC holder with 12 AWG GXL leads**. These are external pack parts, not carrier F1. Manufacturer evidence: [ATOF datasheet, pp1–3](https://www.littelfuse.com/assetdocs/littelfuse_datasheet_287_atof_r2.7.pdf?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40), [FHA holder](https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-ato-fha-datasheet?assetguid=988addec-bfe3-4ea2-9204-e2982cbb488e). Primary PDFs were read through the web tool; direct archival downloads returned HTTP403. Values and URLs are retained in pack-protection-spec.json; no local PDF is fabricated.

Qualified pack maker installs F_PACK between the pack's common positive takeoff and protector B+/P+ path, before any external RUN/CHARGE lead; no branch bypasses it. Keep unfused positive length <=25 mm, separately insulated and mechanically secured. The fuse cannot protect cell-to-cell faults on the parallel bus: the sealed pack maker owns cell matching, individual cell/interconnect fault containment and thermal protection. Do not open the owned pack to retrofit it.

Replace the former16AWG input-harness reference with **>=12AWG copper (3.31 mm²)** on both pack leads, the RUN path and each boost input branch; total round trip <=0.40m. Use the holder's original12AWG leads. Every splice, keyed connector and terminal in this path must be manufacturer-rated/qualified >=30A continuous in the actual enclosure; no Dupont or USB power cable here. Stock EVM power terminals remain; use compatible rated terminations, not unqualified board clips. The5V output18AWG path and carrier layout are unchanged. Fuse ambient <=40°C; verify no nuisance opening over the specified duty cycle. The manufacturer's typical thermal derating is not a guaranteed hold-current measurement.

A15A fuse alone can carry more than15A for a long time. Thus **M_PACK_BREAKER is a second TPS259824OEVM**, at the RUN input before splitting to M_BOOST and M_LOGIC; it does not replace the existing5V M_BREAKER. This closes the moderate-overload gap below the protector's minimum55A trip. [TI device specification](https://www.ti.com/lit/ds/symlink/tps25982.pdf) supports2.7–24V and15A; [EVM guide](https://www.ti.com/lit/pdf/SLUUBX8), schematic/Table4 governs connections.

- Replace R9 with110Ω0.1%0603 Vishay TNPW0603110RBEEA; J10=5–6 only. Nominal Itrip=1460/110+0.11=13.383A. TI's spread is too wide to guarantee the required window from one resistor alone: a qualified assembler must select/trim and verify **12.8–14.8A over3.3–4.2V and0–40°C**; reject a unit outside it. Do not label all stock units compliant. Keep continuous current <=15A.
- R1=100kΩ/R2=69.8kΩ1%0603 (CRCW0603100KFKEA/CRCW060369K8FKEA); nominal UVLO rising2.919V/falling2.676V, independent of the boost's earlier cutoff. Qualified operating input remains>=3.3V; no reliance on operation below the IC's2.7V floor.
- J9OPEN, J11=1–2, J8installed, J4OPEN, J6=1–2, J12=3–4; no programmed blanking, latch-off, intentional reset only. J7=2–3 uses the local LDO for the indicator only; its3.3V output may drop out at low input, and PG is not used for any control. No external VCC_EXT, TP16 load or optional C16. Stock C3=220µF stays fitted.
- Require measured modest-overload opening <=1ms and hard-short opening <=10µs in a current-limited laboratory fixture, with final cables and input capacitors, including startup-into-fault behavior. These are acceptance targets, not guarantees from the typical400ns IC figure. Check both branches together and separately. No repeated auto-restart. The low-voltage modified EVM must pass thermal/startup tests before use; there is no claimed hardware result.

Normal ordering is estimated12.7A pack peak < qualified12.8A minimum RUN trip <=14.8A maximum <15A protected-pack continuous rating <<55A minimum backup protector trip. M_PACK_BREAKER suppresses moderate overloads; F_PACK independently clears major wiring faults or a failed-short electronic path. Neither fuse nor electronic breaker is claimed to have selective priority over the protector during a hard short; whichever safely opens first is acceptable. During CHARGE the RUN branch is physically absent, charger current<=1A and F_PACK remains in circuit.

The sealed assembly is rated>=15A continuous, but **its cells, parallel interconnects and unfused internal terminals must be rated>=30A continuous**, with the following additional fault withstand. This is an acceptance requirement, not an inferred property of140g or a change to assumed cell count. The pack maker must declare prospective short current **<=100A at4.20V**, and substantiate safe cell, protector, holder, connector and insulation behavior through the conservative upper clearing envelope below, or safe opening sooner. Reject a pack lacking that evidence. A15A sticker alone is insufficient. The existing protector's unknown trip delay is not used in the calculation.

|Fault current range|Maximum fuse clearing time used|Required pack/harness withstand through clearing|
|---|---|---|
|<=20.25A|No upper-time claim below135% rating|30A cell/interconnect and harness continuous qualification; RUN breaker limits actual normal assembly to<15A|
|20.25–24A|600s|24A for600s, thermal fault qualification of protector/pack required|
|24–30A|50s|30A for50s, same requirement|
|30–52.5A|5s|52.5A for5s|
|52.5–90A|0.5s|90A for0.5s|
|90–100A|0.1s|100A for0.1s|

Range bounds conservatively apply the lower endpoint's maximum time to the whole range; they do not interpolate a typical curve. For <=5s the largest rectangular fault integral is52.5²×5=13781A²s. An adiabatic copper estimate for3.31mm² gives only about6.3°C conductor rise (using1.724e-8Ωm,8960kg/m³,385J/kgK); connector contacts, fuse-holder heat, cell temperature and long overloads need separate assembled testing. The datasheet's340A²s is **typical pre-arcing**, not a maximum total-clearing rating, and is not substituted for this envelope.100A prospective fault is below the fuse's1000A DC interrupt rating with10× margin; no use with an unbounded/high-energy substitute source.

This completes the specified protection chain, **not validation of the owner's pack**. A qualified closed pack must meet the above cells/interconnect/fault/thermal criteria; keep the unidentified battery disconnected meanwhile. Controlled fault qualification belongs to the pack maker/laboratory, never a request for the owner to short or stall the battery.

## Exact boost configuration

Manufacturer reference: [TI TPS61287EVM-042 guide](https://www.ti.com/lit/ug/slvucw1/slvucw1.pdf), schematic p4/BOM p7–8; [TPS61287 datasheet](https://www.ti.com/lit/ds/symlink/tps61287.pdf), §§6.3.3, 7.2.2.7. Local PDFs are in `sources/`. Stock module is **18 V and cannot be plugged into this carrier**. A qualified electronics assembler makes and labels these changes off-carrier before acceptance:

|Module position|V0.2 value/configuration|Purpose|
|---|---|---|
|R4|59.0 kΩ, 0.1%, Vishay TNPW040259K0BEED, 0402|Upper feedback resistor replaces 243 kΩ|
|R6|14.3 kΩ, 0.1%, Vishay TNPW040214K3BEED, 0402|Lower feedback resistor; replaces 1% original|
|R2|49.9 Ω original, retained|Series loop-injection resistor; included in output calculation|
|R7 / C18 / C3|18 kΩ / 47 nF / 2.2 nF, 0402|Compensation for the actual low-voltage output and carrier capacitance; replaces stock network|
|R5|20 kΩ original, retained|20 A nominal switching valley limit; datasheet minimum 17 A, **not output amperes**|
|JP1|SYNC to GND|Internal oscillator|
|JP3|MODE to GND|Auto PFM; avoids forced reverse current into pack|
|JP2|HIGH, pins2–3; R3 is now39k, not0Ω|Feeds VIN into the EN divider below; do not bypass R3|
|R3 / R10|R3=39 kΩ from VIN to EN; populate R10=20 kΩ EN to AGND; C15=100 nF retained|Typical start 3.63 V, stop 3.42 V at module input; 5.3 µA hysteresis current. Reference resistors CRCW040239K0FKED / CRCW040220K0FKED|

VOUT=1.000×[1+(59000+49.9)/14300]=5.12936 V in PWM. With reference ±1.5%, divider ±0.1% and Auto PFM +1%, calculated unloaded upper bound ≈5.26 V; measured J_PWR must be 4.95–5.25 V in operating conditions. Reject/adjust a high unit before connection. This is a qualification window, not a guaranteed tolerance claim. Intended boost input range is 3.3–4.2 V; measure the EN cutoff over temperature and reject a unit allowing sustained operation below 3.3 V. The protector is a separate deep-discharge backup. Short leads and the original EVM input capacitors remain fitted.

Initial loop sizing uses 3.3 µH original L1 (Coilcraft XGL1060-332MEC), KCOMP=20 A/V, GEA=180 µA/V and TI equations 11–18. The effective output includes original 330+470 µF, ceramics, breaker220µF and carrier1000µF. Conservative sweep: 1.3–2.5 mF, ESR 5–50 mΩ, 0.5–6 A, input 3.3–4.2 V. `tools/board/power-model.py` reports 108 averaged CCM cases; minimum predicted phase margin 66.7°, maximum crossover 1.315 kHz, every crossover below RHP-zero/5 and switching/10. This supports initial component sizing only: **measure Bode margin ≥45°/10 dB and load steps after module modification**, including the real cable, breaker, PFM transition and capacitor tolerances. It is not a switching simulation or measured stability proof.

## Output breaker configuration

[TI TPS259824OEVM guide](https://www.ti.com/lit/pdf/SLUUBX8), Figure 1 and Tables 2–4. Use external module because the carrier's 7 A fuse alone is not a 6 A limiter.

- J1/J3 input; J2/J5 output. Replace selected ILIM resistor **R9 with 232 Ω 1%**, J10=5–6 only. Target approximately 6.4 A; qualify measured overload threshold **6.1–7.2 A** over the intended temperature range. No default 15 A setting.
- J9 OPEN gives zero programmed overload blanking; J11=1–2 latches OFF, no automatic retries; J8 installed disables external handshake. Reset requires an intentional power cycle after fault removal. J12=3–4 sets about 0.5 V/ms rise; ~1.9 mF output requires ~0.95 A startup charging, motors remain disabled.
- Replace UVLO R1=100 kΩ and R2=36.5 kΩ; thresholds nominal rising 4.49 V/falling 4.11 V. A disabled boost can pass raw battery through its power path: the breaker then opens below 4.11 V, so the motors and fan are not left supplied at raw 1S voltage. Verify this on the modified assembly. The carrier ACT_EN default-off mechanism remains independent.
- J7 selects the on-module 3.3 V pull-up (pins 2–3, the three-pin schematic governs over the guide's table typo). Do not connect external VCC_EXT. J4 open; J6=1–2. Stock C3 220 µF retained; optional C16 1800 µF unpopulated; test-load TP16 left open. Stock OVP is 16.7 V and does **not** protect a 5 V servo from a misconfigured boost. Test the isolated assembly before connection.
- The overload is a fast **circuit breaker**, not a precise 6.00 A constant-current supply. At ≤7.2 A, hot-switch instantaneous loss is ≤1.04 W each, allowed only until immediate latch-off; no continuous overload rating is claimed. Confirm trip timing/short fault behavior with a current-limited bench setup before battery acceptance.

## Capacity and pack limits

7×0.8 A servo stall proxy =5.60 A; fan **allocation** 0.30 A including startup; two HC-SR04P allocation 0.030 A (generous relative to 4tronix's <2 mA each); buffer/LDO/bleed allocation 0.030 A. **Carrier total 5.96 A**, leaving 0.04 A at a 6 A design peak. Fan's actual current is unknown; >0.30 A or larger servo stall current needs reassessment. Ordinary motion is estimated at 7×0.25+0.30+0.03+0.03=2.11 A, not measured.

At 5.129 V and 5.96 A plus a 50 mV wiring/breaker allowance, source output is 30.87 W. Use conservative **80% estimated conversion efficiency** for sizing. At boost input 3.3/3.7/4.2 V, load converter input is 11.69/10.43/9.19 A. A separate 5 V/0.50 A LILYGO USB allowance adds 0.95/0.84/0.74 A at the same efficiency. **Boost-input branch sum ≈12.64/11.27/9.93 A; round pack peak upward to12.7A for breaker/indicator overhead**. Require ≥15 A continuous pack/connector rating and transient margin. The 17 A minimum valley limit and 22 A inductor have margin over ≈11.7 A average plus <1 A ripple; the 20 A label was not used as 20 A at 5 V.

12AWG round-trip length <=0.40m gives about2.08mΩ,26.5mV/0.34W at12.7A. F_PACK typical cold4.8mΩ adds61mV/0.77W; require fuse+holder+contacts<=12mΩ assembled (<=152mV/1.94W). The input breaker adds<=6mΩ qualified (<=76mV/0.97W), including low-VIN behavior; this is a test limit, not the12V datasheet RON guarantee. Together with protector20mΩ and wires, peak pack-to-boost drop may reach0.51V;3.3V **at the boost** then needs about3.81V at the pack, so the full peak is unavailable near empty. Early boost UVLO and reduced runtime are expected; do not reduce safety thresholds to compensate. Protection at its published 20 mΩ maximum could add 0.25 V and **3.2 W** at peak; it requires thermal qualification in the sealed pack. Do not promise full stall operation from an enclosed unmeasured assembly. Source loss at 80% is ~7.7 W for load boost and ~0.63 W for logic boost at peak. Reserve airflow/clearance and qualify PCB/module surface temperatures; seven stalled motors are never a continuous operating mode.

Runtime estimate using nominal 3.7 V, pack capacity C Ah, usable fraction u (including early UVLO), efficiency η: t_hours≈3.7×C×u×η/P_5V_total. At estimated ordinary motion P≈13.43 W, **example only C=4 Ah,u=0.6,η=0.8 gives ≈32 min**; peak ≈33.4 W gives ≈13 min energy-only, thermally prohibited as a continuous stall. Neither 4 Ah nor u=0.6 nor cell count is a claim about the owned battery. At 1 A charge, ideal charge time ≥C hours; add CV time. A 4 Ah example needs roughly 4.8 h. Adafruit's fixed 6 h timer means larger/degraded packs require a separately qualified charger; do not repeatedly reset the timer.

## Acceptance still needed

Qualify the owner's closed pack against the selected fuse/RUN-breaker coordination above, or obtain a compliant closed pack; verify actual charge/discharge limits, capacity, polarity and temperature sensing. Charger 6091 must remain in 4.2 V Li-ion mode, set to 1 A only for a pack rated for it, fit its supported 10 kΩ pack thermistor with TH jumper opened, LOAD unused. Verify temperature cutoff using the actual NTC/charger combination. No qualified module chain is evidence that this unidentified pack is safe.

Bench-verify isolated modified boost, breaker, regulator accuracy, UVLO, startup and 0.5→6 A steps before carrier/servo connection. Check LOAD and SERVO spikes ≤5.5 V on braking; the new boost/breaker is not claimed to absorb regeneration. Existing protection/bringup limits still apply. `hardwareTested=false`. Case needs separate supported holders for all three EVMs, the fuse holder and insulated pack/charger wiring; exact EVM envelope/hole locations have not been measured and are not asserted to fit the old reservation.

Modification sourcing: precision divider MPNs appear in externalParts; remaining resistor/capacitor MPNs and package sizes appear in externalModificationParts. Both lists describe off-carrier assembly and must not be treated as PCB placements or LCSC stock commitments.


## Release note 8 — DECIDED power path: two split islands, each its own Pololu U3V70F5 (supersedes the single-converter draft)
Why: no unmodified buyable 1S->5 V converter I could verify is rated >=6 A output (Pololu U3V70F5 page, pololu.com/product/2891: input 2.9–5 V, 5 V +-4 %, 10 A switch, **8 A input for seconds, 7 A prolonged** -> about 4.4 A out at 3.7 V in, ~4.0 A at 3.3 V). So the load is split (finding option (a)); outputs are never paralleled.
| Island | Source | Loads (stall proxy 0.8 A/servo) | Peak | Path |
|---|---|---|---|---|
| A | M_SERVO_BOOST (U3V70F5 #1) -> J_PWR | servos J_S0–J_S2 (CH0–2), turret J_S6 (CH6), fan, 2 sonar, buffers | 4x0.8+0.30+0.06 = **3.56 A** (<=4.0 A) | existing carrier F1 7 A -> Q1 reverse FET -> LOAD_5V -> Q2/Q3 ACT_EN switch (default OFF) -> SERVO_5V |
| B | M_SERVO_BOOST_B (U3V70F5 #2) | servos J_S3–J_S5 (CH3–5) red (V+) wires only | 3x0.8 = **2.4 A** | converter B VOUT -> inline 5 A blade fuse -> red wires of the three plugs; converter B ENABLE gated by ACT_EN (below) |
The carrier PCB is unchanged. For J_S3–J_S5 pull the centre (V+) pin out of each servo plug housing (no soldering, nothing cut on the carrier) and join the three red wires to a small splice that goes to converter B via the 5 A fuse; the carrier V+ pin of those headers stays unconnected, GND and signal still go through the carrier headers, converter B GND and carrier GND meet at the pack negative.
- **Default off / ACT_EN for island B:** U3V70F5 ENABLE is pulled high by an on-board 100 kΩ to VIN (enabled by default, Pololu text) and is forced low under 0.4 V. Add a 4.7 kΩ ENABLE->GND resistor on converter B (VENABLE ≈ 0.17 V, off by default) and wire ENABLE to the ESP32 ACT_EN line (tap J_CTRL pin 6 with a Dupont branch; 3.3 V drive of a pin documented only for "left open = VIN" is GIẢ ĐỊNH: bench-check converter B turns on at 3.3 V; if not, use a 2N7002 pulling ENABLE low from /ACT_EN). Also, PCA_OE_N pull-up still keeps PWM off so servos get no pulses when disabled.
- **Reverse/overload:** each converter has reverse input protection; island A also F1+Q1; island B has the 5 A output fuse. Servo-rail overload on one island does not brown out the other; DevKit logic is a separate USB branch.
- **Pack side (concrete):** one protected 1S pack, both converter inputs in parallel at the pack, never the outputs. Input peak at 3.3 V cell: A 3.56x5/(0.85x3.3)=6.3 A + B 2.4x5/(0.85x3.3)=4.3 A = **10.6 A** (3.7 V: 9.5 A). Each converter input is <=7 A prolonged. Pack protector: **AA Portable Power/BatterySpace PCB-Li-1S15A** (15 A continuous, already in parts.json M_PROTECT) fitted by the pack assembler, with fuse **Littelfuse 0287015.U in 0FHA0002XP** (F_PACK, 15 A, from the earlier chain) at pack positive, 14 AWG <=0.4 m round trip. Cells must be rated >=8 A each continuous for 2 cells in parallel (>=6 A each for 3). The owner's current 140 g pack: model, cell count, rating and protection UNKNOWN — read the labels; if the cells cannot do ~11 A total, a stronger pack is a purchase decision for the owner. M_PACK_BREAKER and the TPS61287 modifications are NOT required any more (optional reference only).
- Ordinary motion ≈ 2.1 A total, so even an unqualified 2-cell pack runs normally; only simultaneous stall of all seven servos needs the ~11 A pack.
- Acceptance (bench, owner): converters unloaded 4.8–5.2 V; 0.5->3.5 A (A) / 2.4 A (B) steps from a bench supply at 3.3–4.2 V; ACT_EN off = 0 V on both islands; spikes <=5.5 V on braking. hardwareTested=false.

### Primary-path ratings and boot behaviour (added after tester notes)
- Fault/connector ratings for the PRIMARY path: pack positive/negative harness and the two converter input branches carry up to 10.6 A: use >=14 AWG and connectors/terminals rated >=15 A continuous (e.g. XT30 is 15 A/30 A burst only if marked; prefer XT60-class 30 A), no Dupont on this path. The F_PACK 15 A ATOF fuse must clear the declared pack prospective short (<=100 A at 4.2 V, per the fuse's 1000 A DC interrupt rating) — the pack maker/owner must state the pack's prospective short current; unknown for the owned pack. The 12 AWG/30 A/fault-table requirements above apply to the optional chain only.
- Island B boot/reset: the ESP32 pin on ACT_EN is high-Z during reset/boot; the 4.7 kΩ ENABLE->GND (and the carrier R4 pull-down on the Q3 side) holds island B OFF until firmware drives ACT_EN high. ENABLE is also pulled to VIN (<=4.2 V) by 100 kΩ (about 9 µA into a 3.3 V pin, harmless). Bench check required: island B stays at 0 V during DevKit boot, reset and with USB unplugged.
