#!/bin/sh
# Fast cut of the app captures: dead time (idle, the agent's wait, static holds) is cut or sped up.
# Run from video/: sh assets/captures/recut.sh. Reads sNN.mp4, writes fast/sNN.mp4.
# Each segment is "start end speed" in source seconds.
set -e
cd "$(dirname "$0")"
mkdir -p fast
cut() {
  name=$1; shift
  f=""; n=0
  for seg in "$@"; do
    set -- $seg
    f="$f[0:v]trim=$1:$2,setpts=(PTS-STARTPTS)/$3[v$n];"
    n=$((n + 1))
  done
  ins=""; i=0
  while [ $i -lt $n ]; do ins="$ins[v$i]"; i=$((i + 1)); done
  ffmpeg -v error -y -i "$name.mp4" -filter_complex "$f${ins}concat=n=$n:v=1,fps=30[o]" \
    -map "[o]" -an -c:v libx264 -crf 16 -g 15 -pix_fmt yuv420p "fast/$name.mp4"
}
# s05: idle, typing x2.4, send, the agent reads x5, the answer and the questions arrive
cut s05 "1.2 1.8 1" "1.8 5.6 2.4" "5.6 6.4 1" "6.4 10.4 5" "10.4 13.5 1"
# s06: one segment for each answer, so that each click lands on the voice (STORYBOARD.md, frame 5).
# Source clicks: 9.53, 10.83, 12.13 s; the message goes 13.73 s; the report card 14.70 s
cut s06 "8.3 9.5 1" "9.5 10.8 1.625" "10.8 12.1 0.9" "12.1 13.7 1.88" "13.7 15.92 1"
# s07: the report opens x1.5, scrolls x1.6, the path and the signal
cut s07 "0.3 2.6 1.5" "2.6 6.4 1.6" "6.4 9.0 1"
# s08: the correction goes, the agent rewrites x3.5, the change marks
cut s08 "0.4 1.4 1" "1.4 5.6 3.5" "5.6 9.4 1"
# s10: the toast, then the click and the alert in the chat
cut s10 "0.8 3.6 1" "6.0 11.0 1"
