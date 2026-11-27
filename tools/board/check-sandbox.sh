#!/bin/bash
# The official publisher keeps its store in <worktree parent>/.kicadpy, which the role sandbox refuses to create.
# Run the unchanged check.py on a copy under $TMPDIR and bring the generated packet back. usage: check-sandbox.sh
set -e;T=${TMPDIR:-/tmp}/boardrun/r001-board;mkdir -p $T
rsync -a --delete --exclude .git --exclude prompts ./ $T/
(cd $T && $KICAD_HARNESS_PYTHON tools/board/check.py) 2>&1 | tee build/board/check-r005-builder.log | tail -${TAILN:-12}
for d in boards build/board manufacturing.json engineering/board-audit.json engineering/native-pads.json engineering/pack-protection-calculations.json engineering/power-calculations.json; do rsync -a $T/$d $(dirname $d)/ ; done
