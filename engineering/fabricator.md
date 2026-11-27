# Fabrication process

2-layer FR4,62×60mm,1.6mm nominal,70µm copper each side (2oz),lead-free HASL. Explicit stackup is in main.kicad_pcb, rules in main.kicad_pro.0.20mm minimum trace and clearance,0.30mm via drill with≥0.15mm annulus,0.40mm copper-edge rule.0.15mm legend strokes,≥0.8mm text. Publisher applies its independent current fabrication floor and parses actual final Gerbers/drills; no native warning is accepted as a pass.

Main6A paths are pours with direct pad connection, not thermal spokes. Ground is a bottom plane with routed local links; servo positive is a top plane; fuse/input and protected LOAD have separate local pours. Through-hole terminal and individual servo headers bridge layers. Exact drill centers, copper, mask, paste, legend and outline must reconcile in the published manufacturing report. Solder mask expansion40µm; no via-in-pad, no controlled impedance, no blind/buried vias, no microvias.

F1 surface-mount fuse is manually fitted. Its missing generic STEP was replaced with a nominal manufacturer-size reference envelope; C1 also uses the correct16mm body height. Sources and tool-limitations.md identify these models. Order quote/DFM and sourcing availability are not performed in this job.
