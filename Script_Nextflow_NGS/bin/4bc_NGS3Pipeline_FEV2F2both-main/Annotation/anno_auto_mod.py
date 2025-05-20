#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:19:59 2023

@author: prabir
"""
import sys
import subprocess
import glob
import pandas as pd
import os
import time
import pandas as pd
import numpy as np
import platform

os.getcwd()

path = os.getcwd()
print("Current working directory is:", os.getcwd())

system_name=os.getlogin()
appses_name = sys.argv[1]
print ("Apps N:", appses_name)
location = sys.argv[2]
project_name = sys.argv[3]

csv = glob.glob(os.path.join(location,"*.csv"))[0]

while True:
    command_stat = 'bs appsession list | grep ' + appses_name+ ' | awk \'{print $6}\'' ' >' 'out.txt'
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
            cmd = f'bs appsession download -i {app_session_id} --extension=hard-filtered.vcf.gz'
            cmd_2 = f"find -type f -name " "*.vcf.gz" " -exec mv {} ./ \;"
            cmd_3 = 'find -type d -name "*_ds*" -exec rm -rf {} \\;'
            with open("output.log", "w") as log_file:
                subprocess.run(cmd, stdout=log_file, stderr=log_file, shell=True)
                subprocess.run(cmd_2, stdout=log_file, stderr=log_file, shell=True)
                subprocess.run(cmd_3, stdout=log_file, stderr=log_file, shell=True)
        command = 'bs appsession list | grep ' + appses_name+ ' | awk \'{print $4}\''
        output = subprocess.check_output(command, shell=True)
        print(output.decode().strip())
        def dragen_metrics(app_session_id):
            cmd_4 = f"bs appsession download -i {app_session_id} --extension=.summary.csv"
            subprocess.run(cmd_4, shell=True)
            cmd_5 = f"find -type f -name " "*.summary.csv" " -exec cp {} ./ \;"
            subprocess.run(cmd_5, shell=True)
            # get a list of all the files in the directory
            files = os.listdir(path)
            # filter out non-CSV files
            filenames = [f for f in files if f.endswith('.csv')]
            # Create an empty list to store the dataframes
            dfs = []
            # Loop through the filenames and read in each CSV file
            for filename in filenames:
                 df = pd.read_csv(filename, skiprows=3)  # skip the first three rows
                 # Select only the second column of the dataframe and append it to the list
                 dfs.append(df.iloc[:, 1])
            # Concatenate the dataframes along the vertical axis
            merged_df = pd.concat(dfs, axis=1)
            # Transpose the dataframe
            transposed_df = merged_df.transpose()
            df_header = []
            # Read in the first CSV file and extract the header from the third row of the first column
            header01 = pd.read_csv(filenames[0], skiprows=3)
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
            # Create QC folder
            os.makedirs(location + '/QC', exist_ok=True)
            os.system("chmod 777 " + location + '/QC')
            # Updated QC
            os.system("python3 /path/4bc_NGS3Pipeline_FEV2F2both/Annotation/qc_upd2.py " + location)
            # Copy the metrics file to the QC folder
            os.system('cp ' + location + '/metrics.csv' + ' ' + location + '/QC')
            qcdf = pd.DataFrame(columns=['Sample Name', "Sequence_length", "Total_Sequences"], dtype=object)
            metrics = pd.read_csv(location + '/QC/metrics.csv', header=0)
            if metrics.columns[0] == 'Sample Name':
                # Change it to Sample ID
                metrics.rename(columns={metrics.columns[0]: 'Sample ID'}, inplace=True)
            qcdf['Sample Name'] = metrics['Sample ID']
            qcdf['Total_Sequences'] = metrics['Total PF read 1']
            qcdf['Sequence_length'] = metrics['Padding size']
            qcdf['Percent duplicate aligned reads'] = metrics['Percent duplicate aligned reads']
            qcdf['Percent Target coverage at 50X'] = metrics['Percent Target coverage at 50X']
            qcdf['Mean target coverage depth'] = metrics['Mean target coverage depth']
            qcdf['Uniformity of coverage (Pct > 0.2*mean)'] = metrics['Uniformity of coverage (Pct > 0.2*mean)']
            qcdf['Fragment length median'] = metrics['Fragment length median']
            qcdf['Total_size'] = 2 * qcdf['Sequence_length'] * qcdf['Total_Sequences'].div(1e9)
            qcdf['qual_Total_size(GB)'] = [0 if i <= 3 else (2 if i >= 4 else 1) for i in list(qcdf['Total_size'])]
            qcdf['qual_Fragment length median'] = [0 if i <= 100 else 2 if i >= 110 else 1 for i in (qcdf['Fragment length median'])]
            qcdf['qual_Percent duplicate aligned reads'] = [0 if i >= 70 else 2 if i <= 40 else 1 for i in list(qcdf['Percent duplicate aligned reads'])]
            qcdf['qual_Percent Target coverage at 50X'] = [0 if i <= 60 else 2 if i >= 90 else 1 for i in list(qcdf['Percent Target coverage at 50X'])]
            qcdf['qual_Mean target coverage depth'] = [0 if i <= 85 else 2 if i >= 100 else 1 for i in list(qcdf['Mean target coverage depth'])]
            qcdf['qual_Uniformity of coverage (Pct > 0.2*mean)'] = [0 if i <= 80 else 2 if i >= 90 else 1 for i in list(qcdf['Uniformity of coverage (Pct > 0.2*mean)'])]
            comments = []
            for i, j, k, l, m in zip(list(qcdf['Fragment length median']), list(qcdf['Percent duplicate aligned reads']), (qcdf['Percent Target coverage at 50X']), list(qcdf['Mean target coverage depth']), list(qcdf['Uniformity of coverage (Pct > 0.2*mean)'])):
                comment = ""
                if i < 100:
                    comment += "Low Fragment Length Median, "
                if i in range(100, 111):
                    comment += "Fragment Length Median on borderline, "
                if j > 50:
                    comment += "High duplicates, "
                if 40 <= j <= 50:
                    comment += "duplicates~40, "
                if l < 100:
                    comment += "Low Mean target coverage depth, "
                if m < 85:
                    comment += "Low Uniformity of coverage, "
                if comment == "":
                    comment = " "
                comments.append(comment.strip())
            qcdf['Comments'] = comments
            column_names = ['qual_Percent duplicate aligned reads', 'qual_Percent Target coverage at 50X', 'qual_Mean target coverage depth', 'qual_Uniformity of coverage (Pct > 0.2*mean)', 'qual_Total_size(GB)']
            qcdf['QC_score'] = qcdf[column_names].sum(axis=1)
            qcdf['QC_status'] = qcdf['qual_Percent duplicate aligned reads'] * qcdf['qual_Percent Target coverage at 50X'] * qcdf['qual_Mean target coverage depth'] * qcdf['qual_Uniformity of coverage (Pct > 0.2*mean)'] * qcdf['qual_Total_size(GB)']
            qcdf['QC_status'] = qcdf['QC_status'].apply(lambda x: 'Fail' if x == 0 else 'Pass')
            header = ["Sample Name", "Total_Sequences", "Percent duplicate aligned reads", "qual_Percent duplicate aligned reads", "Percent Target coverage at 50X", "qual_Percent Target coverage at 50X", "Mean target coverage depth", "qual_Mean target coverage depth", "Uniformity of coverage (Pct > 0.2*mean)", "qual_Uniformity of coverage (Pct > 0.2*mean)", "Fragment length median", "Total_size", "qual_Total_size(GB)", "QC_score", "QC_status", "Comments"]
            qcdf.to_csv(location + '/QC/output.csv', columns=header)
        app_session_id = int(output)
        dragen_metrics(app_session_id)
        download_vcf(app_session_id)
        #Fetching sample details
        file_list=glob.glob("*hard-filtered.vcf.gz")#modified by prabir  WB1R-B-CE-S61.hard-filtered.vcf.gz
        samples=[]
        for file in file_list:
            sample=file.split("/")[-1]
            if '.hard-filtered.vcf.gz' in file_list[0]:
                sample= sample.split(".hard-filtered.vcf.gz")
            else:
                sample= sample.split(".hard")
            samples.append(sample[0])
        samples= pd.unique(samples)
        samples=np.array(samples).tolist()
        #Creating list.txt
        file = open("list.txt", "w+")
        # Saving the array in a text file
        for s in samples:
            file.writelines([s,'\n'])
        file.close()
        ##### testing comparsion  ###
        with open("list.txt", "r") as file1:
             list1 = [line.strip() for line in file1]
        list_1 = 'list.txt'
        os.system('cp '+ list_1 + ' '+ location + '/CNV')
        os.system('cp '+ csv + ' '+ location + '/Gene-Coverage')
        os.system('cp '+ csv + ' '+ location + '/CNV-Coverage')
        os.system('cp '+ csv + ' '+ location+ '/Hotspot')
        loc_ann_file= '/path/4bc_NGS3Pipeline_FEV2F2both/Annotation/annotation.sh' #annotation_threading.py
        loc_confi_file= '/path/4bc_NGS3Pipeline_FEV2F2both/Annotation/config.pl'    
        os.system('cp '+ loc_ann_file + ' '+ './')
        
        os.system('chmod 777 *')
        
        CNV_files=location+'/CNV/cnv_annotation_somatic.sh'
        CNV_config=location+'/CNV/cnv_config_somatic.pl'
        # Read in the file
        with open(CNV_files, 'r') as file :
            filedata = file.read()
        filedata = filedata.replace('{{project_name}}', project_name)
        filedata = filedata.replace('{{location}}', location)
        with open(CNV_files, 'w') as file:
            file.write(filedata)
        chrLenFile = "/path/4bc_NGS3Pipeline_FEV2F2both/CNV/my_genome.fa.fai"
        chrFiles = '/path/files_for_control_freec/chromFa/'
        sambamba = 'path of sambamba'
        with open(CNV_config, 'r') as file_c :
            filedata_config = file_c.read()
        filedata_config = filedata_config.replace('{{chrLenFile}}', chrLenFile)
        filedata_config = filedata_config.replace('{{chrFiles}}', chrFiles)
        filedata_config = filedata_config.replace('{{sambamba}}', sambamba)
        with open(CNV_config, 'w') as file_c:
            file_c.write(filedata_config)
        panel_bed = "/path/4bc_NGS3Pipeline_FEV2F2both/CNV/TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed"
        panelcreate= location +  "/Panel/panelcreate.sh"
        f1= open(panelcreate,"x")
        f1.close()
        f1= open(panelcreate,"w+")
        f1.write("cd "+ location + "/Panel" + '\n')
        for s in samples:
            f1.write("cp "+ location + "/annotation/")
            f1.write(s+ ".hard-filtered.vcf.gz "+ location+ "/Panel"+ '\n')
            f1.write('\n')
            f1.write('chmod 777 *')
            f1.write('\n')
            f1.write("gzip -dk "+ s+ ".hard-filtered.vcf.gz" + '\n')
            f1.write('\n')
            f1.write("/home/ubuntu/Programs/./bedtools.static.binary" + " intersect -header -a " + s+".hard-filtered.vcf -b ")
            f1.write(str(panel_bed)+ " > " + s + ".hard-filtered_TarGT_First_FEV2F2both_panel.vcf")
            f1.write('\n'+ "rm -rf "+ s + ".hard-filtered.vcf")
            f1.write('\n' + "############" +'\n')
        f1.write('\n' +"echo \"######################\"")
        f1.write('\n' +"echo \"######### DONE #########\"")
        f1.write('\n' +"echo \"######################\"")
        f1.close()
        #panelcreate_path= location + "/panel/" + "panelcreate.sh >" + location+ "/panel/panellog.txt"
        def cgi():
            loc_cgi_file='/path/4bc_NGS3Pipeline_FEV2F2both/CGI/cgikrispy2.sh'
            os.system('cp '+ loc_cgi_file + ' ' + location + '/Panel/')
            samples_panel= glob.glob(location+"/Panel/*_panel.vcf")
            samples_panel=np.array(samples_panel).tolist()
            os.system('chmod 777 '+ location + '/Panel/*')
            cgifile=location+'/Panel/cgikrispy2.sh'
            cgi_data = 'path/cgi_commercial1/datasets'
            with open(cgifile, 'r') as file_cgi :
                cgifiledata = file_cgi.read()
                cgifiledata = cgifiledata.replace('{{samplenames}}', str(samples_panel).strip("[]").replace("'","").replace(",",""))
                cgifiledata = cgifiledata.replace('{{location}}', location + '/Panel/')
                cgifiledata = cgifiledata.replace('{{cgi_data}}', cgi_data)
            with open(cgifile, 'w') as file:
                file.write(cgifiledata)
            #os.system("bash "+ cgifile)
            #print("############ CGI analysis completed ###########")
        
        script1="sh annotation.sh"#"python3 splitlist_args.py" #"sh annotation.sh"
        #script1="python3 annotation_threading.py"
        script2=location+"/CNV/cnv_annotation_somatic.sh"
        script3 = location+"/Gene-Coverage/Gene_Coverage_via_Mosdepth_V2.py" 
        script4 = location+"/Panel/panelcreate.sh"
        script5 = location+"/Panel/cgikrispy2.sh"
        script6 = location+"/CNV-Coverage/dragen_output_covrage_file_based_CNV.py"
        #script7 = location+"/Hotspot/Alternate_VariantCaller_to_Hotspot.py"
        script7 = location+"/Hotspot/Alternate_VariantCaller_to_Hotspot_V2_09_Apr_24.py"
        script8 = location+"/Gene-Coverage/Hori_Gen_Coverage.py"
        # Define log file names
        log_file1 = 'annotation.log'
        log_file2 = location+'/CNV/cnv.log'
        log_file3 = location+'/Gene-Coverage/Gene_Cov.log'
        log_file8 = location+'/Gene-Coverage/Hori_Gen_Cov.log'
        log_file4 = location+'/Panel/Panel.log'
        log_file5 = location+'/Panel/CGI.log'
        log_file6 = location+'/CNV-Coverage/CNV-cov.log'
        log_file7 = location+'/Hotspot/hotspot_log.log'
        csv_path = location+'/Gene-Coverage/'
        #csv_path_cnv_cov = location+'/CNV-Coverage/'
        log_file_hotspot = location+'/Hotspot/'
        print ("HOTSPOT:",log_file_hotspot)
        
        print (" ############ Downstream Annalysis is Running ############")
        print ("  ")
        if platform.system() == "Linux":
            terminal_emulator = "gnome-terminal"
        elif platform.system() == "Windows":
            terminal_emulator = "cmd.exe"
        else:
            terminal_emulator = "xterm"  # Default for other platforms
        print ("Emulator Name:",terminal_emulator)
        
        print (" ############ Panel Creating ############")
        subprocess.run(['bash', script4], stdout=open(log_file4, 'a'), stderr=subprocess.STDOUT)
        print (" ############ Panel Created ############")
        print ("  ")
        print (" ############ Annotation initiating ############ ")
        print ("::::Kindly Check - Annotation is Running on another terminal [Terminal Name - ",appses_name, "_Annotation ]::::")
        terminal1 = subprocess.Popen([terminal_emulator,"--title", appses_name+"_Annotation", "--", "bash", "-c", f"{script1}| tee {log_file1}"])
        # Wait for all terminals to finish (optional)
        terminal1.wait()
        print ("  ")
        print ("############- CNV Initiating ############")
        subprocess.run(['sh', script2], stdout=open(log_file2, 'a'), stderr=subprocess.STDOUT)
        print (" ############ CNV Completed ############ ")
        print ("  ")
        
        print("############ Running CGI analysis ###########")
        cgi()
        subprocess.run(['bash', script5], stdout=open(log_file5, 'a'), stderr=subprocess.STDOUT)
        print("############ CGI Completed ###########")
        print ("  ")
        print (" ############ Gene coverage initiating ############")
        subprocess.run(['python3', script3, csv_path, appses_name+".xlsx"], stdout=open(log_file3, 'a'), stderr=subprocess.STDOUT)
        subprocess.run(['python3', script8, csv_path, appses_name], stdout=open(log_file8, 'a'), stderr=subprocess.STDOUT)
        print (" ############ Gene Coverage Completed ############ ")
        print ("  ")
        print (" ############ Hotspot initiating ############")
        subprocess.run(['python3', script7, log_file_hotspot], stdout=open(log_file7, 'a'), stderr=subprocess.STDOUT)
        print (" ")
        print (" ############ HOTSPOT Completed ############ ")
        print (" ############ CNV coverage initiating ############")
        #subprocess.run(['python3', script6, csv_path_cnv_cov, appses_name+".xlsx"], stdout=open(log_file6, 'a'), stderr=subprocess.STDOUT)
        print (" ############ CNV Coverage Completed ############ ")
        remove_file = "rm out.txt"
        os.system(remove_file)
        os.chdir(location)
        os.system("yes | sh " + location + "/basespace.sh")
        print ("   ")
        print ("######################       #########################")
        print (appses_name)
        print ("::::Kindly Check - Annotation is Running on another terminal [Terminal Name - ",appses_name, "_Annotation ]::::")
        print ("######################       #########################")
        print ("   ")
        print ("   ")
        print ("::Checking Parameters::")
        os.system("python3 /path/4bc_NGS3Pipeline_FEV2F2both/Annotation/Parameter_Checker_V2.py "+ appses_name)
        break
    else:
        print ("\n --Sleep-- for 5 min # Analysis Status Will check in every five minutes", " Analysis Status -", data)
        print ("--:: Please do not close the terminal ::--")
        time.sleep(5*60)
        for i in range(5):
        	print(i, "minutes\t", end="", flush=True)
        	time.sleep(5*60)
        remove_file = "rm out.txt"
        os.system(remove_file)