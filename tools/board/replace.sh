#!/bin/bash
# Re-place + strip old copper (one-time migration for release note 8). Output build/board/placed.kicad_pcb
KP=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
cp ${1:-design/main.kicad_pcb} build/board/s1.kicad_pcb
for m in tracks zones draw; do $KP tools/board/rework.py $m build/board/s1.kicad_pcb 2>&1 | grep -v "assert\|leak\|destructor"; done
$KP tools/board/rework.py place build/board/s1.kicad_pcb 2>&1 | grep -v "assert\|leak\|destructor"
