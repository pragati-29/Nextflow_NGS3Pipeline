#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:19:59 2023
@author: Pragati
"""

import subprocess
import glob
import pandas as pd
import os
import time
import numpy as np

os.getcwd()
path = os.getcwd()

# Set location
location = "/home/bioinfoa/Pragati"

# Read the CSV file
path_csv = glob.glob(os.path.join(location, "test_file.csv"))[0]
csv_data = pd.read_csv(path_csv)
#print(csv_data)  # Print CSV content for debugging

# Create the "annotation" directory if it doesn't exist
annotation_dir = os.path.join(location, "annotation")
output_dir = os.path.join(location, "output")
os.makedirs(annotation_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
# Iterate through "appsession_name" column
for appses_name in csv_data["appsession_name"]:
    while True:
        command_stat = '/usr/local/bin/bs appsession list | grep ' + appses_name+ ' | awk \'{print $6}\'' ' >' 'out.txt'
        output_stat = subprocess.check_output(command_stat, shell=True)
        print(output_stat.decode().strip())

        file1=open('out.txt', 'r')
        data=file1.read()
        if "Complete" in data:
            bs_file = open(location+ '/' + "basespace.sh", "w")
            bs_file.write('basemount basespace')
            bs_file.close()
            os.system("chmod 777 "+ location + '/basespace.sh')
            os.chdir(location)
            p = subprocess.Popen(['bash', location + '/basespace.sh'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, error = p.communicate(input='yes\n')
            os.chdir(location + "/annotation")
            def download_vcf(app_session_id):
                # set up the BaseSpace CLI command
                print (app_session_id)
                cmd = f'/usr/local/bin/bs appsession download -i {app_session_id} --extension=hard-filtered.vcf.gz -o {output_dir}'
                cmd_2 = f"find -type f -name " "*.vcf.gz" " -exec mv {{}} {output_dir} \;" #"find -type f -name " "*.vcf.gz" " -exec mv {} ./ \;"
                cmd_3 = 'find -type d -name "*_ds*" -exec rm -rf {} \\;'  #'find -type d -name "*_ds*" -exec rm -rf {} \\;'
                with open("output.log", "w") as log_file:
                    subprocess.run(cmd, stdout=log_file, stderr=log_file, shell=True)
                    subprocess.run(cmd_2, stdout=log_file, stderr=log_file, shell=True)
                    subprocess.run(cmd_3, stdout=log_file, stderr=log_file, shell=True)
            command = '/usr/local/bin/bs appsession list | grep ' + appses_name+ ' | awk \'{print $4}\''
            output = subprocess.check_output(command, shell=True)
            print(output.decode().strip())
            def dragen_metrics(app_session_id):
                cmd_4 = f"/usr/local/bin/bs appsession download -i {app_session_id} --extension=.summary.csv -o {output_dir}"
                subprocess.run(cmd_4, shell=True)
                cmd_5 = f'find {output_dir} -type f -name "*.summary.csv" -exec cp {{}} {output_dir} \;'
                print(cmd_5)
                subprocess.run(cmd_5, shell=True)
                # get a list of all the files in the directory
                files = os.listdir(output_dir)
                print(files)
                # filter out non-CSV files
                filenames = [f for f in files if f.endswith('.csv')]
                # Create an empty list to store the dataframes
                dfs = []
                # Loop through the filenames and read in each CSV file
                for filename in filenames:
                    df = pd.read_csv(output_dir + "/" + filename, skiprows=3)
                    print(df)  # skip the first three rows
                    # Select only the second column of the dataframe and append it to the list
                    dfs.append(df.iloc[:, 1])
                # Concatenate the dataframes along the vertical axis
                merged_df = pd.concat(dfs, axis=1)
                # Transpose the dataframe
                transposed_df = merged_df.transpose()
                df_header = []
                # Read in the first CSV file and extract the header from the third row of the first column
                header01 = pd.read_csv(output_dir + "/" + filenames[0], skiprows=3)
                df_header.append(header01.iloc[:,0])
                header= pd.concat(df_header,axis=1)
                transpose_header = header.transpose()
                merged_df_01 = pd.concat([transpose_header, transposed_df], ignore_index=True)
                # Save the transposed dataframe to a CSV file
                merged_df_01.to_csv(location + "/metrics.csv", index=False, header=False)
                cmd_3 = 'find -type d -name "*_ds*" -exec rm -rf {} \\;'
                subprocess.run(cmd_3, shell=True)
                # filter out non-CSV files
                csv_files = [f for f in files if f.endswith('.summary.csv')]
                # loop through the CSV files and delete them
                for file in csv_files:
                    path_1 = os.path.join(path, file)
                    os.remove(path_1)
            app_session_id = int(output)
            dragen_metrics(app_session_id)
            download_vcf(app_session_id)
            
                # Exit while loop after successful download
            break  

            # Wait for some time before checking status again (prevents excessive polling)
            time.sleep(60)

