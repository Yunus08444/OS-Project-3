
#!/usr/bin/env python3
"""Display the current user's process tree using /proc."""

import os
from pathlib import Path

PROC = Path("/proc")


def read_process(pid):
    """Return process information or None if it disappeared."""
    try:
        status = (PROC / str(pid) / "status").read_text()
        info = {}

        for line in status.splitlines():
            if line.startswith(("Name:", "State:", "PPid:", "VmRSS:", "Uid:")):
                key, _, value = line.partition(":")
                info[key] = value.strip()

        uid = int(info.get("Uid", "0").split()[0])
        if uid != os.getuid():
            return None

        return {
            "pid": pid,
            "ppid": int(info.get("PPid", "0")),
            "name": info.get("Name", "unknown"),
            "state": info.get("State", "unknown"),
            "rss": info.get("VmRSS", "0 kB"),
        }
    except (OSError, ValueError, IndexError):
        return None


def main():
    processes = {}

    for entry in PROC.iterdir():
        if entry.name.isdigit():
            process = read_process(int(entry.name))
            if process is not None:
                processes[process["pid"]] = process

    children = {}
    for process in processes.values():
        children.setdefault(process["ppid"], []).append(process["pid"])

    for pid_list in children.values():
        pid_list.sort()

    def print_tree(pid, prefix="", is_last=True):
        process = processes.get(pid)
        if process is None:
            return

        connector = "└── " if is_last else "├── "
        print(
            f"{prefix}{connector}"
            f"{process['name']} (PID={pid}, "
            f"State={process['state']}, RSS={process['rss']})"
        )

        next_prefix = prefix + ("    " if is_last else "│   ")
        child_pids = children.get(pid, [])

        for index, child_pid in enumerate(child_pids):
            print_tree(
                child_pid,
                next_prefix,
                index == len(child_pids) - 1,
            )

    roots = [
        pid for pid, process in processes.items()
        if process["ppid"] not in processes
    ]

    for root in sorted(roots):
        print_tree(root)


if __name__ == "__main__":
    main()
