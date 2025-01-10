#!/usr/bin/env bash

set -e

time_command=(/usr/bin/time -v)

# gdb_cmd=(gdb --batch --quiet)
# gdb_cmd=(gdb --batch --quiet -ex "b break_here" -ex "run" -ex "ctx" /root/pwndbg/tests/gdb-tests/tests/binaries/telescope_binary.out)
# gdb_cmd=(gdb --batch --quiet -ex "b break_here" -ex "set syntax-highlight off" -ex "run" -ex "ctx" /root/pwndbg/tests/gdb-tests/tests/binaries/telescope_binary.out)
gdb_cmd=()
# gdb_cmd=(gdb -nx --batch --quiet)
# gdb_cmd=(gdb -nx --batch --quiet -ex "b break_here" -ex "run" -ex "info frame" /root/pwndbg/tests/gdb-tests/tests/binaries/telescope_binary.out)

echo "GDB command: ${gdb_cmd[@]}"

target_gdb() {
    sudo chrt -f 99 "${time_command[@]}" "${gdb_cmd[@]}" 2>&1 > /dev/null | grep wall | grep -o ": .*" | cut -d: -f3
}

target_ctx() {
    # /root/pwndbg/profiling/profile.sh /root/pwndbg/profiling/context.py | grep 'context.py:[0-9]\+(context)' | tr -s ' ' | cut -d' ' -f5
    gdb --batch --quiet -ex "b break_here" -ex "set confirm off" -ex "run" -ex "profiler start" -ex "run" -ex "ctx" -ex "profiler stop" /root/pwndbg/tests/gdb-tests/tests/binaries/telescope_binary.out | cut -d: -f2
}

runtime_sum=0
runtime_sum_sq=0

if [ "$RUNONLY" ]; then
    exec "${gdb_cmd[@]}"
    exit $?
fi

N="${1:-5}"
echo "Profiling (time in seconds). N=$N"
if (($N == 0)); then
    exit 0
fi

for ((i = 1; i <= N; i++)); do
    runtime="$(target_gdb)"
    # runtime="$(target_ctx)"

    echo "Run $i: $runtime"

    runtime_sum=$(echo "$runtime_sum + $runtime" | bc)
    runtime_sum_sq=$(echo "scale=8; $runtime_sum_sq + $runtime * $runtime" | bc)
    # echo "DEBUG" $runtime_sum $runtime_sum_sq
done

avg=$(echo "scale=8; $runtime_sum / $N" | bc)
printf "Average: %.3f\n" "$avg"
# echo "DEBUG $runtime_sum_sq / $N - $avg * $avg"
printf "Standard deviation: %.4f\n" "$(echo "scale=8; sqrt($runtime_sum_sq / $N - $avg * $avg)" | bc)"
