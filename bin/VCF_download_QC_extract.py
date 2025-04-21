#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import glob
import pandas as pd
import os
import time
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Process CSV file and perform analysis.")
    parser.add_argument("--location", required=True, help="Directory location where files are stored")
    parser.add_argument("--csv_file", required=True, help="Path to the CSV file")
    
    args = parser.parse_args()
    location = args.location
    csv_file = args.csv_file
    
    # Read the CSV file
    csv_data = pd.read_csv(csv_file)
    
    # Create necessary directories
    annotation_dir = os.path.join(location, "annotation")
    output_dir = os.path.join(location, "output")
    os.makedirs(annotation_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Iterate through "appsession_name" column
    for appses_name in csv_data["appsession_name"]:
        while True:
            command_stat = '/usr/local/bin/bs appsession list | grep ' + appses_name+ ' | awk \'{print $6}\'' ' >' 'out.txt'
            subprocess.run(command_stat, shell=True)
            
            with open('out.txt', 'r') as file1:
                data = file1.read()
            
            if "Complete" in data:
                bs_file_path = os.path.join(location, "basespace.sh")
                with open(bs_file_path, "w") as bs_file:
                    bs_file.write('basemount basespace')
                
                os.system(f"chmod 777 {bs_file_path}")
                os.chdir(location)
                
                p = subprocess.Popen(['bash', bs_file_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, error = p.communicate(input='yes\n')
                os.chdir(annotation_dir)
                
                def download_vcf(app_session_id):
                    print(app_session_id)
                    cmd = f'/usr/local/bin/bs appsession download -i {app_session_id} --extension=hard-filtered.vcf.gz -o {output_dir}'
                    cmd_2 = f'find {output_dir} -type f -name "*.vcf.gz" -exec mv {{}} {output_dir} \;'
                    cmd_3 = 'find -type d -name "*_ds*" -exec rm -rf {} \\;'
                    
                    with open("output.log", "w") as log_file:
                        subprocess.run(cmd, stdout=log_file, stderr=log_file, shell=True)
                        subprocess.run(cmd_2, stdout=log_file, stderr=log_file, shell=True)
                        subprocess.run(cmd_3, stdout=log_file, stderr=log_file, shell=True)
                
                command = '/usr/local/bin/bs appsession list | grep ' + appses_name+ ' | awk \'{print $4}\''
                output = subprocess.check_output(command, shell=True)
                app_session_id = int(output.strip())
                
                def dragen_metrics(app_session_id):
                    cmd_4 = f"/usr/local/bin/bs appsession download -i {app_session_id} --extension=.summary.csv -o {output_dir}"
                    subprocess.run(cmd_4, shell=True)
                    cmd_5 = f'find {output_dir} -type f -name "*.summary.csv" -exec cp {{}} {output_dir} \;'
                    subprocess.run(cmd_5, shell=True)
                    
                    files = os.listdir(output_dir)
                    filenames = [f for f in files if f.endswith('.csv')]
                    
                    dfs = []
                    for filename in filenames:
                        df = pd.read_csv(os.path.join(output_dir, filename), skiprows=3)
                        dfs.append(df.iloc[:, 1])
                    
                    merged_df = pd.concat(dfs, axis=1).transpose()
                    header = pd.read_csv(os.path.join(output_dir, filenames[0]), skiprows=3).iloc[:, 0]
                    merged_df_01 = pd.concat([header.to_frame().transpose(), merged_df], ignore_index=True)
                    merged_df_01.to_csv(os.path.join(location, "metrics.csv"), index=False, header=False)
                    
                    cmd_3 = 'find -type d -name "*_ds*" -exec rm -rf {} \\;'
                    subprocess.run(cmd_3, shell=True)
                    
                    for file in filenames:
                        os.remove(os.path.join(output_dir, file))
                
                dragen_metrics(app_session_id)
                download_vcf(app_session_id)
                break
            
            time.sleep(60)

if __name__ == "__main__":
    main()
