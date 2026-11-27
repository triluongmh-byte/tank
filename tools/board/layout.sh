#!/bin/bash
# placement -> Freerouting (all cores; repeated stochastic attempts until KiCad DRC is clean) -> finish (pours, legends) -> DRC.
# Skips everything when layout.json, rework/route code and the netlist are unchanged and build/board/finished.kicad_pcb is clean.
KP=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
S=$(shasum -a 256 tools/board/layout.json tools/board/rework.py tools/board/finish.py tools/board/strip.py tools/board/route.py tools/board/route.sh build/board/main.net | shasum -a 256 | cut -c1-16)
if [ "$(cat build/board/layout.stamp 2>/dev/null)" = "$S" ] && [ -f build/board/finished.kicad_pcb ]; then echo "layout inputs unchanged; reuse build/board/finished.kicad_pcb"; exit 0; fi
tools/board/place.sh || exit 1
for try in 215 205 210 220 230 240 200 225 235 245; do
  export CLR=$try FORCE=1
  tools/board/route.sh | tail -1
  $KP tools/board/strip.py build/board/routed.kicad_pcb build/board/stripped.kicad_pcb 2>&1 | grep -v 'assert\|leak\|destr\|Debug'
  $KP tools/board/finish.py build/board/stripped.kicad_pcb build/board/finished.kicad_pcb 2>&1 | grep -v "assert\|leak\|destr"
  R=$(N=0 tools/board/quickdrc.sh build/board/finished.kicad_pcb | head -1);echo "clearance $try: $R"
  [ "$R" = "{}" ] && { echo $S > build/board/layout.stamp; exit 0; }
done
exit 1
