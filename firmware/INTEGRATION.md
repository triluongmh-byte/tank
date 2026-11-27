# Cross-team firmware interface

Contract SHA256: `a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810`.
Applied release note 1 `925a86e2870b7771a6384cfc1df26373c453eb6b1641875672edac24955a0f9b`, then note 2 `970ada06549758588b018766ef373dfc419cde2300bb9706493bc9685ee53bda`. Chain tip supplied by lead: `7e7f4c02aacd7022041e5024e73ea9147258d8258d998e0ca41ff001d1ca0658`. HC-SR04P replaces HC-SR04; 5 V fan connects to LOAD_5V/GND without a GPIO; the owned parallel-18650 1S pack requires verified protection/charge/5 V conversion. Firmware GPIOs/behavior are unchanged; existing binary is retained.

Run `python3 firmware/reconcile.py` in the integrated workspace. It reads KiCad 9/10 connector pad nets directly from `design/main.kicad_pcb`, compares every contract J_* pad plus J_FAN, checks GPIO definitions and sealed hash, and writes `firmware/reports/integration.json`. Board-documented RAW PWM inputs are accepted only after checking each matching U1 input/output pair, J_Sx signal and U1 OE/supply/ground nets. A named NC pad must remain isolated. Missing board/case inputs are explicitly pending. Final integration can require both with `--require-board --require-case`; mismatches exit nonzero. This supplements, and never replaces, native PCB gates.

Current board SHA256: `32c6e9ddaff8cda39247f041256be938245a10eed1f25d6ff7fb60e6135eb7cb`. All electrical connector checks pass; case is unavailable. Board DEVIATIONS.md items 1/3 document buffered PWM nets and connector placement changes. WIRING.md now describes actual 2×6 J_CTRL/J_PCA and row directions. This electrical check does not approve the geometry deviation: lead/case must reconcile actual STEP, cable routes and connector access. No case source or production angle was inferred.

The case team's current collision/motion evidence should be accompanied by `case/firmware-limits.json`:

```json
{
  "contractSha256": "a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810",
  "status": "passed",
  "turretYawMinDeg": -30,
  "turretYawMaxDeg": 30,
  "checkedFiles": {"case/reports/motion.json": "<actual SHA256>"}
}
```

The angles above are an interchange example, not accepted limits. Evidence must cover the real motion including wires. After reviewing the real checked range, firmware updates `tank/mechanical_limits.h` within -70..+70 degrees (a conservative engineering target), reruns reconciliation, host tests and target compile. Default is center-only and `AUTO SCAN` returns `ERR MOTOR case-range`. No unchecked overview/box becomes a motion limit. Noninteger ranges should be rounded inward in the handoff so the firmware and report match exactly.

Mechanical calibration to confirm: turret positive command is positive yaw about +Z; sonar F at zero looks -Y; sonar R looks +Y. Six wheel direction signs and neutral widths are measured individually. Firmware targets do not prove actual angles or clearance.

Current autonomous behavior is deliberately limited to centered, slow advance followed by a power-cut stop on obstruction/unknown. No automatic blind turn or reverse is attempted. Stationary scan is implemented separately, available only after checked yaw bounds are imported. The reference host's fixed old MAC/receipt/CAPS must not be reused; use firmware/host/tank_transport.py with new explicit authorization and actual target identity.
