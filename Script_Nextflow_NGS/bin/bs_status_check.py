#!/usr/bin/env python3

import sys
import os
import time
import subprocess
import pandas as pd
import argparse

CHECK_INTERVAL_MIN = 5
MOUNT_TIMEOUT_SEC = 60  # Max time to wait for mount readiness

def find_completed_appsession(appsession_name: str, project_name: str) -> str:
    """Return the most recent completed AppSession ID for given name and project."""
    cmd = (
        f"bs list appsessions --project-name '{project_name}' | "
        f"grep '{appsession_name}' | grep 'Complete' | "
        "awk -F'|' '{print $3}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | head -n 1"
    )
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return ""

def ensure_mount_point(mount_dir: str) -> None:
    """Create the mount directory if it does not exist."""
    if not os.path.exists(mount_dir):
        os.makedirs(mount_dir)

def mount_basespace(mount_dir: str) -> None:
    """Unmount if already mounted, then mount BaseSpace at the given directory and verify readiness."""
    if os.path.ismount(mount_dir):
        print(f"[Unmounting] {mount_dir}")
        subprocess.run(["basemount", "--unmount", mount_dir], check=True)

    print(f"[Mounting] BaseSpace to {mount_dir}")
    try:
        result = subprocess.run(["basemount", mount_dir], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to mount BaseSpace:\n{e.stderr}")
        sys.exit(1)

    waited = 0
    while not os.path.ismount(mount_dir):
        print(f"⏳ Waiting for BaseSpace mount at {mount_dir}... ({waited}/{MOUNT_TIMEOUT_SEC}s)")
        time.sleep(2)
        waited += 2
        if waited >= MOUNT_TIMEOUT_SEC:
            print(f"❌ ERROR: Timeout waiting for BaseSpace to mount at {mount_dir}")
            sys.exit(1)

    print(f"[✔] BaseSpace mount ready at {mount_dir}")

def main():
    parser = argparse.ArgumentParser(description="Check BaseSpace AppSession statuses and mount BaseSpace.")
    parser.add_argument("manifest", help="Sample manifest CSV file")
    parser.add_argument("--mount-dir", default="basespace", help="Directory to mount BaseSpace")

    args = parser.parse_args()

    manifest_path = args.manifest
    mount_dir = args.mount_dir

    # Load manifest CSV
    try:
        df = pd.read_csv(manifest_path)
    except Exception as e:
        print(f"❌ Failed to read manifest file '{manifest_path}': {e}")
        sys.exit(1)

    completed = set()
    ensure_mount_point(mount_dir)

    try:
        while True:
            print("\n🔁 Checking BaseSpace AppSession statuses...\n")
            any_incomplete = False

            for idx, row in df.iterrows():
                app_name = str(row["appsession_name"]).strip()
                project = str(row["Project_name"]).strip()

                if app_name in completed:
                    continue

                print(f"> Checking: {app_name} in {project}")
                app_id = find_completed_appsession(app_name, project)

                if app_id:
                    print(f"[✔] Complete: {app_name} → AppSession ID: {app_id}")
                    mount_basespace(mount_dir)
                    completed.add(app_name)
                else:
                    print(f"[✖] Not complete yet: {app_name}")
                    any_incomplete = True

            if not any_incomplete:
                print("\n✅ All analyses are complete and BaseSpace mounts are ready.")
                break

            print(f"\n⏳ Sleeping for {CHECK_INTERVAL_MIN} minutes before next check...")
            time.sleep(CHECK_INTERVAL_MIN * 60)

    finally:
        # Write status file in the current working directory (Nextflow work dir)
        status_file = os.path.join(os.path.dirname(manifest_path), "bs_status_complete.txt")
        with open(status_file, "w") as f:
            if 'any_incomplete' in locals() and any_incomplete:
                f.write("BaseSpace check ran but some sessions are still pending.\n")
            else:
                f.write("BaseSpace mounting complete\n")
        print(f"\n📄 Status written to {status_file}")

if __name__ == "__main__":
    main()

