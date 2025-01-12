#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys

import config

WORKSPACE = os.path.expanduser(config.WORKSPACE)

# command line arguments
if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <cid>", file=sys.stderr)
    sys.exit(1)

cid = sys.argv[1] # Content ID

# read json file
with open(f"{WORKSPACE}/{cid}.json", "r") as f:
    resource = json.load(f)

cmd = "bash"  # 実行するコマンド
try:
    # コマンドを起動し、標準入力を開く
    process = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE, text=True)

    # サブプロセスの標準入力にデータを書き込む
    process.stdin.write('''
set -eu
TMOZ=$(mktemp -d moz.XXXXXX)
trap 'rm -rf $TMOZ' EXIT
function squoosh () {
# source width height target
  local s=$1 w=$2 h=$3 t=$4
  local x=${s##*/}
  local b=${x%.*}
  sharp --quality 75 --mozjpeg --input $s --output $t.jpg  -- resize $w $h
  sharp --quality 45           --input $s --output $t.avif -- resize $w $h
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
  convert $s -gravity center -crop "$p:$q^+0+0" $TMOZ/$b.jpeg
  sharp --quality 75 --mozjpeg --input $TMOZ/$b.jpeg --output $t.jpg -- resize $w $h
  rm -f $TMOZ/$b.jpeg
}
''')

    d = f'{WORKSPACE}/{cid}'
    s = resource['cover']['file']
    t = resource['cover']['hash']

    process.stdin.write(f'''
mkdir -p {d}/2x
squoosh {s} 120 90 {d}/S{t}
squoosh {s} 240 180 {d}/2x/S{t}
squoosh_crop {s} 320 180 {d}/W{t}
squoosh_crop {s} 320 240 {d}/F{t}
squoosh_crop {s} 240 240 {d}/Q{t}
''')
    
    for s in resource['section']:
        for p in s['photo']:
            s = p['file']
            t = p['hash']
            w, h = (270, 180) if p['width'] > p['height'] else (180, 270)
            process.stdin.write(f"squoosh {s} {w} {h} {d}/{t}\n")
            process.stdin.write(f"squoosh {s} {2*w} {2*h} {d}/2x/{t}\n")
                      
    process.stdin.close()  # 入力を閉じる

    # コマンドの終了を待つ
    process.wait()
except OSError as e:
    print(f"Can't execute {cmd}: {e}")

# __END__