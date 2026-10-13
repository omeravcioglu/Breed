#!/usr/bin/env bash
# Usage: ./run.sh [build_city.py args...]   e.g. ./run.sh --layout layout_test --phases terrain,roads --renders map
cd "$(dirname "$0")"
BL="/c/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe"
"$BL" -b --factory-startup --python build_city.py -- "$@" 2>&1 | awk '/CITYGEN_REPORT_BEGIN/{p=1;next}/CITYGEN_REPORT_END/{p=0}p||/Traceback|Error|error:|CITYGEN_FAILED|WARN/'
