#!/bin/bash
# placement only (strip already done): re-apply layout.json to build/board/s1.kicad_pcb
KP=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$KP tools/board/rework.py place build/board/s1.kicad_pcb 2>&1 | grep -v "assert\|leak\|destructor"
