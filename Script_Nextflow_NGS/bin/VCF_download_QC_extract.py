#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import os
import time
import pandas as pd
import shutil

def wait_until_complete(appsession_name):
    while True:
        status_cmd = f"/usr/local/bin/bs appsession list | grep {appsession_name} | awk '{{print $6}}'"
        status = subprocess.getoutput(status_cmd).strip()
        print(f"AppSession: {appsession_name} | Status: {status}")
        if "Complete" in status:
            return
        time.sleep(60)

def get_appsession_id(appsession_name):
    id_cmd = f"/usr/local/bin/bs appsession list | grep {appsession_name} | awk '{{print $4}}'"
    return subprocess.getoutput(id_cmd).strip()

def download_all_summaries(appsession_id, temp_dir):
    """Downloads all .summary.csv files from a session into a temp folder"""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    download_cmd = f"/usr/local/bin/bs appsession download -i {appsession_id} --extension=.summary.csv -o {temp_dir}"
    subprocess.run(download_cmd, shell=True)

def filter_and_copy_samples(temp_dir, qc_dir, allowed_sample_ids):
    """Move only required sample summary files based on Sample_ID list"""
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".summary.csv"):
                sample_name = file.split(".summary.csv")[0]
                if sample_name in allowed_sample_ids:
                    src = os.path.join(root, file)
                    dst = os.path.join(qc_dir, f"{sample_name}_summary.csv")
                    shutil.copy(src, dst)

def merge_summaries(qc_dir, output_file):
    summary_files = sorted([f for f in os.listdir(qc_dir) if f.endswith("_summary.csv")])
    if not summary_files:
        print("No summary files to merge.")
        return

    dfs = []
    for file in summary_files:
        df = pd.read_csv(os.path.join(qc_dir, file), skiprows=3)
        sample_name = file.replace("_summary.csv", "")
        df.columns = [f"{sample_name}_{col}" for col in df.columns]
        dfs.append(df.iloc[:, 1])  # assuming 2nd column has metric value

    merged = pd.concat(dfs, axis=1).transpose()
    header = pd.read_csv(os.path.join(qc_dir, summary_files[0]), skiprows=3).iloc[:, 0]
    final_df = pd.concat([header.to_frame().transpose(), merged], ignore_index=True)
    final_df.to_csv(output_file, index=False, header=False)
    print(f"\nMerged QC file written to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Download QC summary only for listed samples.")
    parser.add_argument("--location", required=True, help="Base working directory")
    parser.add_argument("--csv_file", required=True, help="CSV file with 'appsession_name' and 'Sample_ID' columns")
    args = parser.parse_args()

    location = args.location
    csv_file = args.csv_file
    qc_dir = os.path.join(location, "QC")
    temp_dir = os.path.join(location, "temp_download")
    os.makedirs(qc_dir, exist_ok=True)

    # Clean previous output
    for f in os.listdir(qc_dir):
        if f.endswith("_summary.csv"):
            os.remove(os.path.join(qc_dir, f))

    csv_data = pd.read_csv(csv_file)
    if not {"appsession_name", "Sample_ID"}.issubset(csv_data.columns):
        print("ERROR: CSV must contain 'appsession_name' and 'Sample_ID' columns.")
        return

    grouped = csv_data.groupby("appsession_name")

    for appsession_name, group in grouped:
        print(f"\nProcessing AppSession: {appsession_name}")
        wait_until_complete(appsession_name)
        appsession_id = get_appsession_id(appsession_name)

        sample_ids = group["Sample_ID"].tolist()
        download_all_summaries(appsession_id, temp_dir)
        filter_and_copy_samples(temp_dir, qc_dir, sample_ids)

    merge_summaries(qc_dir, os.path.join(location, "metrics.csv"))

if __name__ == "__main__":
    main()