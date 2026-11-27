#!/usr/bin/env bash
# Pet Tank: rebuild every generated output from the committed sources.
#   ./build.sh                  # board -> case -> firmware
#   ./build.sh board            # only the listed stages (case also needs build/board/main-contract.step)
#   ./build.sh case firmware
# No network installs. Nothing is flashed, printed, uploaded or ordered.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$PWD

die() { echo "build.sh: $*" >&2; exit 1; }
need_env() { [ -n "${!1:-}" ] || die "missing env $1 ($2)"; [ -x "${!1}" ] || die "$1=${!1} is not executable"; }

STAGES=("$@")
[ ${#STAGES[@]} -eq 0 ] && STAGES=(board case firmware)
for s in "${STAGES[@]}"; do
  case "$s" in board|case|firmware) ;; *) die "unknown stage '$s' (use board, case, firmware)";; esac
done
want() { local s; for s in "${STAGES[@]}"; do [ "$s" = "$1" ] && return 0; done; return 1; }
# Pull in earlier stages whose outputs a requested stage reads:
# firmware reads case/reports/turret_yaw.json (turret limits); case reads the board STEP.
if want firmware && ! want case && [ ! -f case/reports/turret_yaw.json ]; then
  echo "build.sh: firmware needs case/reports/turret_yaw.json -> adding stage case"; STAGES=(case "${STAGES[@]}")
fi
if want case && ! want board && [ ! -f case/ref/board/main-contract.step ]; then
  echo "build.sh: case needs case/ref/board/main-contract.step -> adding stage board"; STAGES=(board "${STAGES[@]}")
fi

# The sealed team contract lives in contract/; the case tools read it at the root.
[ -f contract/PILOT_CONTRACT.json ] || die "contract/PILOT_CONTRACT.json missing"
[ -e PILOT_CONTRACT.json ] || ln -s contract/PILOT_CONTRACT.json PILOT_CONTRACT.json

KICAD_CLI=${KICAD_CLI:-$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)}

stage_board() {
  echo "== board: checks, manufacturing packet, STEP"
  need_env KICAD_HARNESS_PYTHON "host Python with kicadpy (set by Harness)"
  need_env KICAD_CASE_PYTHON "CadQuery Python (set by Harness)"
  [ -x "$KICAD_CLI" ] || die "kicad-cli not found; install KiCad 9 or set KICAD_CLI"
  mkdir -p build/board
  # Publish first: tools/board/review.py (run by check.py) reads boards/main.board.json.
  "$KICAD_HARNESS_PYTHON" -m kicadpy.publish --manufacturing design/main.kicad_pro
  "$KICAD_HARNESS_PYTHON" tools/board/check.py
  "$KICAD_CLI" pcb export step --force --include-tracks --include-pads --include-zones \
    --include-silkscreen --include-soldermask -o build/board/main-native.step design/main.kicad_pcb
  "$KICAD_CASE_PYTHON" tools/board/step-frame.py >/dev/null
  # Hand the populated carrier STEP to the case team and re-bind its hashes (a rebuild changes the bytes).
  cp build/board/main-contract.step case/ref/board/main-contract.step
  cp engineering/board-geometry.json case/ref/board/board-geometry.json
  (cd case/ref/board && shasum -a 256 board-geometry.json main-contract.step > SHA256SUMS)
}

stage_case() {
  echo "== case: CAD, checks, plates, slicing, overview"
  need_env KICAD_CASE_PYTHON "CadQuery Python (set by Harness)"
  "$KICAD_CASE_PYTHON" case/build.py
  "$KICAD_CASE_PYTHON" tools/case/fit_checks.py
  "$KICAD_CASE_PYTHON" tools/case/v5_compare.py
  "$KICAD_CASE_PYTHON" tools/case/turret_limits.py
  "$KICAD_CASE_PYTHON" tools/case/docs/make_steps.py
  "$KICAD_CASE_PYTHON" tools/case/docs/make_plates.py
  if [ -x /Applications/BambuStudio.app/Contents/MacOS/BambuStudio ]; then
    "$KICAD_CASE_PYTHON" tools/case/docs/slice_and_verify.py
  else
    die "Bambu Studio not found at /Applications/BambuStudio.app (needed to slice case/print/*.3mf)"
  fi
  "$KICAD_CASE_PYTHON" -m kicadpy.case_overview .
  # Handwired layout (case/out/parts.json: nativePCBCheckerApplies false): print check, not the PCB-fit check.
  "$KICAD_CASE_PYTHON" -m kicadpy.case check-print .
}

stage_firmware() {
  echo "== firmware: host tests, ESP32 compile"
  command -v arduino-cli >/dev/null || die "arduino-cli not found (needs installed core esp32:esp32@2.0.14)"
  command -v python3 >/dev/null || die "python3 not found"
  python3 firmware/check.py
  python3 firmware/build.py
}

want board && stage_board
want case && stage_case
want firmware && stage_firmware
echo "build.sh: done (${STAGES[*]}) in $ROOT"
