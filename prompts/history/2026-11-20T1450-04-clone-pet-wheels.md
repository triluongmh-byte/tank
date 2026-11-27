nói lead clone cái bánh xe của con claude-pet qua 2 cái nữa, tao 
  có 4 cái rồi

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- The user already owns 4 printed claude-pet wheels and wants the tank to use that same wheel design,
  with 2 more cloned so there are 6.
- Source of the claude-pet wheels: user's repo https://gitlab.com/triluongmh/claude-pet.git, commit
  3c5e9457995933f800be0044858d026ef6001d83, folder pet-case/case/wheels (recorded as the pet's source in
  /Users/macbookpro/harnesses/claude-pet-case/host/recovery.json). Hash-checked copies (SHA256SUMS) are in
  /Users/macbookpro/harnesses/pet-tank/prompts/assets/claude-pet-wheels-3c5e945/ : STEP+STL of
  07_drive_wheel L/R, 08_drive_guide L/R, 09_horn_cap L/R, 10_idler_wheel L/R, 11_idler_guide L/R,
  ref_servo_L, ref_horn_L, plus drive-assembly.md/.png, hardware-list.md, hardware.json, axle-detail.png.
- Measured from the STLs: wheels 07/10 are Ø54 × 25 mm wide (spiked tread); guides 08/11 Ø46.4 × 8.4 mm;
  horn cap 09 Ø46.4 × 2.8 mm; reference SG90-class horn Ø35 × 5.1 mm.
- In the pet, the 4 wheels are 2 servo-driven fronts (07 + 08 horn slot + 09 nut cap, clamped by 2× M3×16
  around the stock servo horn, servo centre screw through the middle — see drive-assembly.md) and 2 rear
  idlers (10 + 11) on an axle. The tank needs all 6 wheels on 360° servos, so the 2 owned idler wheels may
  lack the servo-horn interface. Which owned wheel is which is not confirmed by the user; treat as GIẢ ĐỊNH.
