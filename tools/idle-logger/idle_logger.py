#!/usr/bin/env python3
"""
idle_logger - records how long a lab PC has been idle (no input), once per interval.

Privacy: only the time of the last input event is used. Key codes, key content
and mouse positions are never read or stored.

Output: one CSV row per interval:
  time (ISO 8601), node, idle_seconds, user_sessions, cpu_percent

Run as root (needs /dev/input access). Install: sudo apt install python3-evdev python3-psutil
Get permission from the lab administrators before installing on lab machines.
"""
import csv
import os
import selectors
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime

import evdev
import psutil
from evdev import ecodes

NODE = socket.gethostname().split(".")[0]
OUT = os.environ.get("IDLE_LOG", f"/var/log/idle_{NODE}.csv")
INTERVAL = int(os.environ.get("IDLE_INTERVAL", "60"))   # seconds between rows
RESCAN = 30                                              # seconds between device rescans


def user_sessions():
    """Number of logged-in user sessions (GUI or SSH), excluding the greeter."""
    n = 0
    out = subprocess.run(["loginctl", "list-sessions", "--no-legend"],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        sid = line.split()[0]
        info = subprocess.run(["loginctl", "show-session", sid, "-p", "Class", "-p", "State"],
                              capture_output=True, text=True).stdout
        props = dict(p.split("=", 1) for p in info.split() if "=" in p)
        if props.get("Class") == "user" and props.get("State") != "closing":
            n += 1
    return n


class Inputs:
    def __init__(self):
        self.sel = selectors.DefaultSelector()
        self.paths = set()

    def rescan(self):
        for path in evdev.list_devices():
            if path in self.paths:
                continue
            try:
                dev = evdev.InputDevice(path)
            except OSError:
                continue
            caps = dev.capabilities()
            keys = caps.get(ecodes.EV_KEY, [])
            if (ecodes.KEY_A in keys or ecodes.EV_REL in caps
                    or ecodes.BTN_LEFT in keys or ecodes.BTN_TOUCH in keys):
                self.sel.register(dev, selectors.EVENT_READ, dev)
                self.paths.add(path)
            else:
                dev.close()

    def poll(self, timeout):
        """Return the newest input-event timestamp seen, or None. Contents are discarded."""
        last = None
        for key, _ in self.sel.select(timeout):
            dev = key.data
            try:
                for ev in dev.read():
                    if ev.type in (ecodes.EV_KEY, ecodes.EV_REL, ecodes.EV_ABS):
                        last = ev.timestamp() if last is None else max(last, ev.timestamp())
            except BlockingIOError:
                pass
            except OSError:
                self.sel.unregister(dev)
                self.paths.discard(dev.path)
                dev.close()
        return last


def main():
    signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))
    inputs = Inputs()
    inputs.rescan()
    last_input = time.time()          # rows before the first input underestimate idle time
    last_scan = last_row = 0.0
    new = not os.path.exists(OUT)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "node", "idle_seconds", "user_sessions", "cpu_percent"])
            f.flush()
        while True:
            if time.time() - last_scan > RESCAN:
                inputs.rescan()
                last_scan = time.time()
            ts = inputs.poll(1.0)
            if ts is not None:
                last_input = max(last_input, ts)
            now = time.time()
            if now - last_row >= INTERVAL:
                last_row = now
                w.writerow([datetime.fromtimestamp(now).isoformat(timespec="seconds"), NODE,
                            int(now - last_input), user_sessions(),
                            psutil.cpu_percent(interval=None)])
                f.flush()


if __name__ == "__main__":
    main()
