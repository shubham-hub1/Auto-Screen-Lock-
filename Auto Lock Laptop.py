#!/usr/bin/env python3
# -------------------------------------------------------------
# bluetooth_lock.py – Windows PC lock when a Bluetooth device goes out of range
# -------------------------------------------------------------
# Requirements (install once):
#   pip install bleak pywin32
# -------------------------------------------------------------

import sys
import time
import threading
import argparse
import ctypes
from typing import Optional

# -------------------------------------------------
# 1️⃣ Windows lock helper
# -------------------------------------------------
def lock_workstation() -> None:
    """Lock the Windows session using the native Win32 API."""
    if ctypes.windll.user32.LockWorkStation():
        print("[INFO] Workstation locked.")
    else:
        print("[WARN] Unable to lock workstation via ctypes.")


# -------------------------------------------------
# 2️⃣ Bluetooth discovery utilities (Bleak)
# -------------------------------------------------
try:
    from bleak import BleakScanner
except ImportError:
    print("[ERROR] bleak is not installed. Run:")
    print("    py -3 -m pip install bleak")
    sys.exit(1)


async def _scan_once() -> list[tuple[str, str]]:
    """Return a list of (address, name) tuples for discovered devices."""
    devices = await BleakScanner.discover(timeout=4.0)
    return [(d.address, d.name or "Unknown") for d in devices]


def find_device_by_address(target_addr: str) -> Optional[str]:
    """Return the device name if the MAC address is currently discoverable."""
    import asyncio
    try:
        result = asyncio.run(_scan_once())
        for addr, name in result:
            if addr.upper() == target_addr.upper():
                return name
    except Exception as e:
        print(f"[WARN] BLE scan error: {e}")
    return None


def find_device_by_name(target_name: str) -> Optional[str]:
    """Return the MAC address if a device with the given name is discovered."""
    import asyncio
    try:
        result = asyncio.run(_scan_once())
        for addr, name in result:
            if name and name.lower() == target_name.lower():
                return addr
    except Exception as e:
        print(f"[WARN] BLE scan error: {e}")
    return None


# -------------------------------------------------
# 3️⃣ Monitoring thread (unchanged)
# -------------------------------------------------
class BluetoothWatcher(threading.Thread):
    def __init__(self, mac: Optional[str], name: Optional[str],
                 interval: float, timeout_sec: float):
        super().__init__(daemon=True)
        self.mac = mac
        self.name = name
        self.interval = max(0.1, interval)
        self.timeout_sec = max(1.0, timeout_sec)
        self.last_seen = time.time()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        print("[INFO] Bluetooth watcher started.")
        while not self._stop_event.is_set():
            try:
                if self.mac:
                    present = find_device_by_address(self.mac) is not None
                else:
                    present = find_device_by_name(self.name) is not None
            except Exception as e:
                print(f"[WARN] Bluetooth scan error: {e}")
                present = False

            if present:
                self.last_seen = time.time()
            else:
                elapsed = time.time() - self.last_seen
                if elapsed >= self.timeout_sec:
                    print(f"[INFO] Device missing for {elapsed:.1f}s – locking.")
                    lock_workstation()
                    self.last_seen = time.time()   # reset timer after lock

            time.sleep(self.interval)


# -------------------------------------------------
# 4️⃣ CLI entry‑point (unchanged)
# -------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Lock a Windows PC when a specific Bluetooth device goes out of range."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--mac", help="Bluetooth MAC address (e.g. AA:BB:CC:DD:EE:FF).")
    group.add_argument("--name", help="Bluetooth device name (e.g. 'MyPhone').")
    parser.add_argument("--interval", type=float, default=5.0,
                        help="Seconds between scans (default 5).")
    parser.add_argument("--timeout", type=float, default=15.0,
                        help="Seconds device may be missing before lock (default 15).")
    return parser.parse_args()


def main():
    args = parse_args()
    watcher = BluetoothWatcher(mac=args.mac, name=args.name,
                               interval=args.interval, timeout_sec=args.timeout)
    watcher.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping Bluetooth monitor…")
        watcher.stop()
        watcher.join()
        print("[INFO] Exited cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        main()
    else:
        print("[ERROR] This script runs on Windows only.")
        sys.exit(1)
