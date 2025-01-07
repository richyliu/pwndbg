# Results of line profiling

Results of using line-profile package can be found in [line_profiling.txt](line_profiling.txt). The majority of the time is spent in the `GDB.setup` function, which imports gdblib and aglib, as well as initializes commands. Note that the profiler itself also has some overhead, which skews results.

I have selected several places for refactoring which are easy for reducing load times:
- in [pwndbg/hexdump.py](pwndbg/hexdump.py), lazy load `enhex` from `pwndbg.commands.windbg`
- in [pwndbg/lib/functions.py](pwndbg/lib/functions.py), dynamically creating the `functions` table
See the `profile-lazy1` branch for the implementation of these changes.

Unfortunately, testing reveals only a 1% speedup (and somewhat inconsistent results, too). I believe a 15% speedup should be possible, given the profiling results. It is unclear whether my measurement methodology is inaccurate or if the profiling is unreliable (due to the overhead of the profiler).

## Testing methodology

I am using the following command to measure total startup time:

```sh
sudo chrt -f 99 su - user -c '/usr/bin/time -v -- gdb --batch --quiet' 2>&1 >/dev/null
```
and taking the "wall clock" time.

The `sudo chrt -f 99` part configures the linux scheduler so that no other processes run concurrently (by giving this process a high priority). Then, I use `su - user -c` to run the command as user `user` (as opposed to `root`). Finally the `time` utility is invoked with the `gdb --batch --quiet`, which tells gdb to start up and then immediately exit. As an alternative to `time`, I have also tried using `perf stat`.

I do multiple runs and then take the average. Usually an initial warm-up run is needed, as poetry may attempt to update dependencies, which can take a significant amount of time.

## Next steps

Loading the `pwndbg.aglib.*` submodules lazily should significantly decrease startup times. Profiling indicates at least 54% of the load time is spent on loading these modules, most of which are not actually necessary at startup.
