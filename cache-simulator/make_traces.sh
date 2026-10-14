#!/bin/bash
# Records REAL memory traces from compiled C programs using Valgrind (Linux/WSL/macOS-with-valgrind).
# Setup (Ubuntu/WSL):  sudo apt install valgrind gcc
# Usage:  ./make_traces.sh matmul      (needs traces/matmul.c)
set -e
p=$1
gcc -O0 -g -o traces/$p traces/$p.c
valgrind --tool=lackey --trace-mem=yes ./traces/$p 2>&1 >/dev/null | grep -E '^ [LSM] ' | gzip > traces/$p.trace.gz
echo "Wrote traces/$p.trace.gz  ($(zcat traces/$p.trace.gz | wc -l) data accesses)"
