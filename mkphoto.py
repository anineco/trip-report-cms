#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path
import subprocess
import sys

from config import DIST_DIR, WORK_DIR

# command line arguments
out_dir = DIST_DIR
if len(sys.argv) == 2:
    cid = sys.argv[1]  # Content ID
elif len(sys.argv) == 3 and sys.argv[1] == "-w":
    out_dir = WORK_DIR
    cid = sys.argv[2]
else:
    print(f"Usage: {sys.argv[0]} [-w] <cid>", file=sys.stderr)
    sys.exit(1)

# read json file
with open(os.path.join(WORK_DIR, f"{cid}.json"), "r") as f:
    resource = json.load(f)

# provide shell script to squoosh images
cmd = ["bash", "-eu"]
try:
    process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, text=True)
    process.stdin.write(
        """
TMOZ=$(mktemp -d moz.XXXXXX)
trap 'rm -rf $TMOZ' EXIT
function squoosh () {
# source width height target
  local s=$1 w=$2 h=$3 t=$4
  npx sharp --quality 75 --mozjpeg --input $s --output $t.jpg  -- resize $w $h
  npx sharp --quality 45           --input $s --output $t.avif -- resize $w $h
}
function squoosh_crop () {
# source width height target
  local s=$1 w=$2 h=$3 t=$4
  local x=${s##*/}
  local b=${x%.*}
  # calculate LCD
  local p=$w q=$h
  local r=$[$p%$q]
  while [ $r -gt 0 ]; do
    p=$q q=$r r=$[$p%$q]
  done
  p=$[$w/$q]
  q=$[$h/$q]
  magick $s -gravity center -crop "$p:$q^+0+0" $TMOZ/$b.jpeg
  npx sharp --quality 75 --mozjpeg --input $TMOZ/$b.jpeg --output $t.jpg -- resize $w $h
  rm -f $TMOZ/$b.jpeg
}
"""
    )

    d = f"{out_dir}/{cid}"
    s = resource["cover"]["file"]
    t = resource["cover"]["hash"]

    process.stdin.write(
        f"""
mkdir -p {d}/2x
squoosh {s} 120 90 {d}/S{t}
squoosh {s} 240 180 {d}/2x/S{t}
squoosh_crop {s} 320 180 {d}/W{t}
squoosh_crop {s} 320 240 {d}/F{t}
squoosh_crop {s} 240 240 {d}/Q{t}
"""
    )

    for s in resource["section"]:
        for p in s["photo"]:
            s = p["file"]
            t = p["hash"]
            # NOTE: image size is fixed to 270x180 or 180x270
            w, h = (270, 180) if p["width"] > p["height"] else (180, 270)
            process.stdin.write(f"squoosh {s} {w} {h} {d}/{t}\n")
            process.stdin.write(f"squoosh {s} {2*w} {2*h} {d}/2x/{t}\n")

    process.stdin.close()
    process.wait()
except OSError as e:
    print(f"Can't execute {cmd[0]}: {e}", file=sys.stderr)

# __END__
