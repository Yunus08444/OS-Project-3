
#!/usr/bin/env python3
"""Run commands in child processes using fork() and exec()."""

import argparse
import os
import time


def run_command(command, index):
    start = time.monotonic()
    pid = os.fork()

    if pid == 0:
        try:
            os.execvp(command[0], command)
        except OSError as error:
            print(f"Child {index}: cannot execute command: {error}", flush=True)
            os._exit(127)

    _, status = os.waitpid(pid, 0)
    elapsed = time.monotonic() - start

    if os.WIFEXITED(status):
        return_code = os.WEXITSTATUS(status)
    elif os.WIFSIGNALED(status):
        return_code = 128 + os.WTERMSIG(status)
    else:
        return_code = -1

    print(
        f"Child {index}: PID={pid}, "
        f"exit_code={return_code}, time={elapsed:.3f}s"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run a command in N child processes."
    )
    parser.add_argument("-n", "--num", type=int, default=3,
                        help="number of child processes (default: 3)")
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="command to execute; put it after --")

    args = parser.parse_args()

    if args.num < 1:
        parser.error("--num must be at least 1")

    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    if not command:
        parser.error("provide a command after --, e.g. -- /bin/echo Hello")

    for index in range(1, args.num + 1):
        run_command(command, index)


if __name__ == "__main__":
    main()
