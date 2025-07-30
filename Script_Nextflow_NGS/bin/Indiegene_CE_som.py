#!/usr/bin/env python3

import pandas as pd
import subprocess
import argparse
import os
import sys
import time

MOUNT_TIMEOUT_SEC = 60
CHECK_INTERVAL_SEC = 300  # Check every 5 minutes

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

def ensure_mount_point(mount_dir: str):
    if not os.path.exists(mount_dir):
        os.makedirs(mount_dir)

def mount_basespace(mount_dir: str):
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

def wait_for_appsession_completion(appsession_name, project_name):
    print(f"\n🔁 Monitoring AppSession: {appsession_name}")
    while True:
        app_id = find_completed_appsession(appsession_name, project_name)
        if app_id:
            print(f"✅ AppSession '{appsession_name}' completed → ID: {app_id}")
            return app_id
        else:
            print(f"⏳ AppSession '{appsession_name}' is not complete yet. Retrying in {CHECK_INTERVAL_SEC // 60} minutes...")
            time.sleep(CHECK_INTERVAL_SEC)

def main():
    parser = argparse.ArgumentParser(description="Launch and check AppSession, then mount BaseSpace.")
    parser.add_argument("sample_file", help="Input CSV manifest")
    parser.add_argument("--mount-dir", default="basespace", help="Mount directory for BaseSpace")
    args = parser.parse_args()

    file1 = pd.read_csv(args.sample_file)
    grouped_samp = file1.groupby(["Capturing_Kit", "Somatic_Germline"])["Biosample_ID"].apply(
        lambda x: ",".join(map(str, map(int, x)))
    )

    for idx, row in file1.iterrows():
        test_name = row["Test_Name"]
        capr_kit = row["Capturing_Kit"]
        proj_id = row["Project_ID"]
        appsession_name = row["appsession_name"]
        bed_id = row["bed_id"]
        liq_tm = row["liquid_tumor"]
        vc_af_call = row["vc-af-call-threshold"]
        vc_af_filt = row["vc-af-filter-threshold"]
        cnv_base = row["cnv_baseline_Id"]
        noise_base = row["baseline-noise-bed"]
        germ_som = row["Somatic_Germline"]
        vc_type = row["vc_type"]
        sample_type = row["Sample_Type"]
        project_name = row["Project_name"]

        if "somatic" in germ_som and "INDIEGENE" in test_name and "DNA" in sample_type:
            if capr_kit == "CE":
                try:
                    biosamp_CE_som = grouped_samp.loc["CE", "somatic"]
                except KeyError:
                    print("⚠️ Skipping row due to missing grouped biosample info.")
                    continue

                print(f"\n🔹 Launching AppSession for: {appsession_name}")
                command_bs_launch = (
                    f'bs launch application -n "DRAGEN Enrichment" '
                    f"--app-version 3.9.5 -o project-id:{proj_id} "
                    f"-o app-session-name:{appsession_name} -l {appsession_name} "
                    f"-o vc-type:{vc_type} -o ht-ref:hg19-altaware-cnv-anchor.v8 "
                    f"-o fixed-bed:custom -o target_bed_id:{bed_id} "
                    f"-o input_list.sample-id:biosamples/{biosamp_CE_som} "
                    f"-o picard_checkbox:1 -o liquid_tumor:{liq_tm} "
                    f"-o af-filtering:1 -o vc-af-call-threshold:{vc_af_call} "
                    f"-o vc-af-filter-threshold:{vc_af_filt} -o sv_checkbox:1 "
                    f"-o sq-filtering:1 -o tmb:1 -o vc-hotspot:27723066652 "
                    f"-o {noise_base} -o vcf-site-filter:1 -o cnv_checkbox:1 "
                    f"-o cnv_ref:1 -o cnv_segmentation_mode:cbs -o cnv-filter-qual:50.0 "
                    f"-o {cnv_base} -o cnv_gcbias_checkbox:1 -o hla:1 -o nirvana:1 "
                    f'-o commandline-disclaimer:true -o arbitrary:"--read-trimmers:adapter --trim-adapter-read1" '
                    f"-o additional-file:25600057590 -o automation-sex:unknown"
                )

                result = subprocess.run(command_bs_launch, shell=True, capture_output=True, text=True)
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)

                # Wait for AppSession to complete
                app_id = wait_for_appsession_completion(appsession_name, project_name)

                # Mount BaseSpace
                ensure_mount_point(args.mount_dir)
                mount_basespace(args.mount_dir)

if __name__ == "__main__":
    main()
