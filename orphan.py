
#!/usr/bin/env python3
"""Demonstrate an orphan process on Linux."""

import os
import time


def main():
    pid = os.fork()

    if pid == 0:
        # Child waits for its parent to exit.
        time.sleep(2)
        print(
            f"Child PID={os.getpid()}, "
            f"new PPID={os.getppid()}",
            flush=True,
        )
        time.sleep(5)
        print("Orphan demonstration finished.", flush=True)
        os._exit(0)

    print(
        f"Parent PID={os.getpid()}, child PID={pid}",
        flush=True,
    )
    print("Parent exits; child will continue running.", flush=True)
    os._exit(0)


if __name__ == "__main__":
    main()
