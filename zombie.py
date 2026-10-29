
#!/usr/bin/env python3
"""Demonstrate a zombie process on Linux."""

import os
import time


def main():
    pid = os.fork()

    if pid == 0:
        print(f"Child exits immediately: PID={os.getpid()}", flush=True)
        os._exit(0)

    print(f"Parent PID={os.getpid()}, child PID={pid}", flush=True)
    print("Child has exited, but parent has not called wait().")
    print("Check the child state in another terminal:")
    print(f"  ps -o pid,ppid,stat,cmd -p {pid}", flush=True)

    try:
        time.sleep(20)
    finally:
        # Reap the child so no zombie remains after the demo.
        os.waitpid(pid, 0)
        print("Parent collected the child. Zombie removed.", flush=True)


if __name__ == "__main__":
    main()
