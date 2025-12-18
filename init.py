#!/usr/bin/env python3
"""
Change the UID of the linux user `postgres` based on the environment variable
POSTGRES_UIDNUMBER and then enter an infinite sleep loop.

Usage:
    sudo POSTGRES_UIDNUMBER=123 python3 change_postgres_uid.py
"""

import os
import sys
import time
import pwd
import subprocess
from typing import Optional


def get_env_uid() -> Optional[int]:
    """Return the integer value of POSTGRES_UIDNUMBER if it exists and is valid.

    Returns:
        int: the UID from the environment variable (already validated)
        None: if the variable is not set or is invalid
    """
    env_val = os.getenv("POSTGRES_UIDNUMBER")
    if env_val is None:
        print("INFO: Environment variable POSTGRES_UIDNUMBER is not set – "
              "no UID change will be performed.")
        return None

    env_val = env_val.strip()
    if not env_val:
        print("WARNING: POSTGRES_UIDNUMBER is set but empty – ignoring.")
        return None

    try:
        uid = int(env_val)
    except ValueError:
        print(f"ERROR: POSTGRES_UIDNUMBER='{env_val}' is not a valid integer.")
        return None

    if not (50 <= uid <= 1000):
        print(f"ERROR: UID {uid} is out of the allowed range (50‑1000).")
        return None

    return uid


def user_exists(username: str) -> bool:
    """Check whether a given username exists on the system."""
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def uid_in_use(uid: int) -> bool:
    """Check whether the desired UID is already assigned to another user."""
    try:
        pwd.getpwuid(uid)
        return True
    except KeyError:
        return False


def change_postgres_uid(new_uid: int) -> bool:
    """Attempt to change the uid of the `postgres` user to `new_uid`.

    Returns:
        bool: True on success, False otherwise.
    """
    # Safety checks before invoking the privileged command
    if not user_exists("postgres"):
        print("ERROR: User `postgres` does not exist on this system.")
        return False

    if uid_in_use(new_uid):
        # If the UID belongs to `postgres` already, it's fine; otherwise warn.
        current = pwd.getpwuid(new_uid).pw_name
        if current != "postgres":
            print(f"ERROR: UID {new_uid} is already used by user `{current}`.")
            return False
        else:
            print(f"INFO: UID {new_uid} is already the UID of `postgres`; nothing to do.")
            return True

    # Build the usermod command
    cmd = ["usermod", "-u", str(new_uid), "postgres"]
    try:
        print(f"INFO: Running command: {' '.join(cmd)}")
        # Using check=True will raise CalledProcessError on non‑zero exit status
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"SUCCESS: UID of `postgres` changed to {new_uid}.")
        return True
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode().strip()
        print(f"ERROR: Failed to change UID. Command output: {err}")
        return False
    except PermissionError:
        print("ERROR: Permission denied – you must run this script as root.")
        return False


def infinite_sleep():
    """Sleep forever, but in small intervals to stay responsive to signals."""
    print("INFO: Entering infinite sleep loop (press Ctrl‑C to exit).")
    try:
        while True:
            # Sleep for an hour each iteration – adjust if you prefer a different cadence
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\nINFO: Received KeyboardInterrupt – exiting.")
        sys.exit(0)


def main():
    # Quick sanity check: are we root?
    if os.geteuid() != 0:
        print("WARNING: This script is not running as root. UID changes will likely fail.")
    
    uid = get_env_uid()
    if uid is not None:
        # Attempt the UID modification
        changed = change_postgres_uid(uid)
        if not changed:
            print("WARNING: UID change was not successful. Continuing to sleep loop anyway.")
    else:
        print("INFO: No valid POSTGRES_UIDNUMBER supplied – skipping UID change.")

    # Finally, stay alive forever
    infinite_sleep()


if __name__ == "__main__":
    main()
