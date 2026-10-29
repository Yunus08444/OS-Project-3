
#!/usr/bin/env python3
"""Demonstrate Copy-on-Write after fork() on Linux."""

import os
import sys
import time

SIZE_MB = 64
PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")


def read_memory():
    """Read memory statistics from /proc/self/smaps_rollup."""
    stats = {}

    try:
        with open("/proc/self/smaps_rollup", encoding="utf-8") as file:
            for line in file:
                key, separator, value = line.partition(":")
                if separator and key in {
                    "Rss",
                    "Pss",
                    "Private_Dirty",
                    "Shared_Clean",
                    "Shared_Dirty",
                }:
                    stats[key] = int(value.split()[0])
    except OSError as error:
        print(f"Cannot read memory statistics: {error}", flush=True)

    return stats


def show_memory(label, stats):
    print(f"\n{label}", flush=True)
    for key, value in stats.items():
        print(f"  {key}: {value} kB", flush=True)


def main():
    if not hasattr(os, "fork"):
        print("This demonstration requires Linux and fork().")
        sys.exit(1)

    print(f"Parent PID={os.getpid()}", flush=True)
    print(f"Allocating {SIZE_MB} MiB...", flush=True)

    data = bytearray(SIZE_MB * 1024 * 1024)

    # Touch every page so the memory is physically allocated.
    for offset in range(0, len(data), PAGE_SIZE):
        data[offset] = 1

    show_memory("Parent before fork", read_memory())

    pid = os.fork()

    if pid == 0:
        try:
            print(f"\nChild PID={os.getpid()}", flush=True)
            show_memory("Child before modification", read_memory())

            # Write once per page. CoW creates private pages for the child.
            for offset in range(0, len(data), PAGE_SIZE):
                data[offset] = 2

            show_memory("Child after modification", read_memory())
            print("\nChild changed its pages; parent's data is unchanged.",
                  flush=True)
        finally:
            os._exit(0)

    _, status = os.waitpid(pid, 0)

    if os.WIFEXITED(status):
        print(f"\nChild exit code: {os.WEXITSTATUS(status)}", flush=True)

    show_memory("Parent after child exits", read_memory())
    print(f"Parent data at first byte: {data[0]}", flush=True)
    print("Expected value: 1", flush=True)


if __name__ == "__main__":
    main()
