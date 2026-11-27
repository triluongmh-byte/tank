#!/bin/bash
# placed.kicad_pcb -> routed.kicad_pcb with all CPU cores (Freerouting). Skips when placed board + router unchanged.
set -e;KP=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
IN=${1:-build/board/placed.kicad_pcb};OUT=${2:-build/board/routed.kicad_pcb}
H=$(shasum -a 256 tools/board/layout.json tools/board/rework.py build/board/main.net tools/board/route.py | shasum -a 256 | cut -c1-16)-$CLR
if [ -z "$FORCE" ] && [ -f $OUT ] && [ "$(cat build/board/route.hash 2>/dev/null)" = "$H" ]; then echo "route inputs unchanged; reuse $OUT"; exit 0; fi
$KP tools/board/route.py export $IN 2>&1 | grep -v "assert\|leak\|destructor" || true
TC=/Users/macbookpro/projects/autonomous-circuit-kicad-v11/toolchain/freerouting
JAVA=$(ls $TC/jdk*/Contents/Home/bin/java)
rm -f build/board/main.ses
$JAVA -Djava.awt.headless=true -jar $TC/freerouting-2.4.1.jar -de build/board/main.dsn -do build/board/main.ses -mp 30 -mt $(sysctl -n hw.ncpu) > build/board/router.log 2>&1
$KP tools/board/route.py import $OUT 2>&1 | grep -v "assert\|leak\|destructor" || true
echo $H > build/board/route.hash # one stochastic attempt; layout.sh loops until DRC is clean
