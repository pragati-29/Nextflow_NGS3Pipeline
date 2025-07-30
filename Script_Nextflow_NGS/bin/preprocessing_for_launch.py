#!/usr/bin/env python3
import sys
import os
import time
import subprocess
import pandas as pd
import argparse

CHECK_INTERVAL_MIN = 5
MOUNT_TIMEOUT_SEC = 60

def find_completed_appsession(appsession_name: str, project_name: str) -> str:
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
    os.makedirs(mount_dir, exist_ok=True)

def mount_basespace(mount_dir: str) -> None:
    if os.path.ismount(mount_dir):
        print(f"[Unmounting] {mount_dir}")
        subprocess.run(["basemount", "--unmount", mount_dir], check=True)

    print(f"[Mounting] BaseSpace to {mount_dir}")
    try:
        subprocess.run(["basemount", mount_dir], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to mount BaseSpace:\n{e.stderr}")
        sys.exit(1)

    waited = 0
    while not os.path.ismount(mount_dir):
        print(f"⏳ Waiting for BaseSpace mount at {mount_dir}... ({waited}/{MOUNT_TIMEOUT_SEC}s)")
        time.sleep(2)
        waited += 2
        if waited >= MOUNT_TIMEOUT_SEC:
            print(f"❌ Timeout waiting for BaseSpace to mount at {mount_dir}")
            sys.exit(1)

    print(f"[✔] BaseSpace mount ready at {mount_dir}")

def main():
    parser = argparse.ArgumentParser(description="Launch TARGET_FIRST AppSessions and monitor them.")
    parser.add_argument("sample_file", help="Path to the input CSV file")
    parser.add_argument("--mount-dir", default="basespace", help="Directory to mount BaseSpace")
    args = parser.parse_args()

    try:
        file1 = pd.read_csv(args.sample_file)
    except Exception as e:
        print(f"❌ Failed to read sample file: {e}")
        sys.exit(1)

    project = file1["Project_name"].iloc[0]
    status_filename = f"{project.upper()}_bs_status_complete.txt"
    status_file = os.path.join(os.path.dirname(args.sample_file), status_filename)

    grouped_samp = file1.groupby(["Capturing_Kit", "Somatic_Germline"])['Biosample_ID'].apply(
        lambda x: ",".join(map(str, map(int, x)))
    )

    ensure_mount_point(args.mount_dir)

    for idx, row in file1.iterrows():
        test_name = row['Test_Name']
        capr_kit = row['Capturing_Kit']
        proj_id = row['Project_ID']
        appsession_name = row['appsession_name']
        bed_id = row['bed_id']
        liq_tm = row['liquid_tumor']
        vc_af_call = row['vc-af-call-threshold']
        vc_af_filt = row['vc-af-filter-threshold']
        vc_type = row['vc_type']
        germ_som = row['Somatic_Germline']
        sample_type = row['Sample_Type']
        project_name = row['Project_name']

        if not isinstance(appsession_name, str) or appsession_name.strip() == "":
            print(f"⚠️ Skipping row {idx} due to missing appsession name.")
            continue

        if "somatic" in germ_som and "TARGET_FIRST" in test_name and "DNA" in sample_type:
            if "FEV2F2both" in capr_kit:
                biosamp_key = ("FEV2F2both", "somatic")
                biosamp_FEV2 = grouped_samp.get(biosamp_key)
                if not biosamp_FEV2:
                    print(f"⚠️ Missing grouped biosamples for {biosamp_key}. Skipping.")
                    continue

                command_bs_launch = (
                    f"bs launch application -n 'DRAGEN Enrichment' --app-version 3.9.5 "
                    f"-o project-id:{proj_id} -o app-session-name:{appsession_name} -l {appsession_name} "
                    f"-o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 -o fixed-bed:custom "
                    f"-o target_bed_id:{bed_id} -o input_list.sample-id:biosamples/{biosamp_FEV2} "
                    f"-o picard_checkbox:1 -o liquid_tumor:{liq_tm} -o af-filtering:1 "
                    f"-o vc-af-call-threshold:{vc_af_call} -o vc-af-filter-threshold:{vc_af_filt} "
                    f"-o sv_checkbox:1 -o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 "
                    f"-o vcf-site-filter:1 -o hla:1 -o nirvana:1 -o commandline-disclaimer:true "
                    f"-o arbitrary:'--read-trimmers:adapter --trim-adapter-read1' "
                    f"-o additional-file:25600057590 -o automation-sex:unknown"
                )

                print(f"\n🚀 Launching AppSession: {appsession_name}")
                launch_result = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                print("STDOUT:", launch_result.stdout.strip())
                print("STDERR:", launch_result.stderr.strip())

                print(f"🔁 Monitoring AppSession: {appsession_name}")
                while True:
                    app_id = find_completed_appsession(appsession_name, project_name)
                    if app_id:
                        print(f"[✔] AppSession {appsession_name} completed → ID: {app_id}")
                        mount_basespace(args.mount_dir)
                        break
                    else:
                        print(f"⏳ AppSession {appsession_name} not complete yet. Retrying in {CHECK_INTERVAL_MIN} minutes...")
                        time.sleep(CHECK_INTERVAL_MIN * 60)

    # Write status if completed
    with open(status_file, "w") as f:
        f.write(f"BaseSpace mounting complete for all TARGET_FIRST FEV2F2both samples in project {project}.\n")
    print(f"\n📄 Status written to {status_file}")

if __name__ == "__main__":
    main()
