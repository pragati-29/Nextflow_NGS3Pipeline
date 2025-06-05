# Nextflow_NGS3Pipeline 
## Aim:- Implementation of NGS3Pipeline in Nextflow 
## Overview 
This Nextflow pipeline is designed for comprehensive downstream analysis of next-generation sequencing (NGS) data. It supports the execution of multiple processes CNV, gene coverage, hotspot, QC, and DNA fusion. You will need to provide a csv file where you will keep all the information regarding samples and in output folder you will get subfolders for each process (CNV, Hotspot, QC, DNA Fusion, Gene coverage).  
## Requirements: -
  * Nextflow
  * Python3
    * subprocess
    * pandas
    * re
    * csv
    * datetime 
  * Basespace Illumina access
  * Java (For Nextflow installation)
## Nextflow installation
  * Install SDKMAN:
      curl -s https://get.sdkman.io | bash
  * Install JAVA:
      sdk install java 17.0.10-tem
  * Install Nextflow:
      curl -s https://get.nextflow.io | bash
  * Make Nextflow executable:
      chmod +x nextflow
  * sudo mv nextflow /usr/local/bin/
## Basespace installation
  * Install bs: 
      wget https://github.com/basespace/basespace-cli/releases/download/v0.9.93/bs-linux
  * Make it executable: 
      chmod +x bs-linux
  * Move: 
      sudo mv bs-linux /usr/local/bin/bs
  * login: 
      bs auth
## Clone GitHub repository
   - Go to Source Control of VS Code
   - Click on clone
   - Paste link of your repository
   - Clone using terminal: git clone "repository"
## Input:
  * Folder of fastq files (All types)
  * csv file
  * Output Folder
## Output:
  * Renaming of samples for uploading in basespace
  * Uploaded samples in basespace projects
  * Analysis of samples
## Sections of the Script:
#### Parameter Definitions
    params.input_dir 
    params.sample_file 
    params.output_dir 
    params.project (Use this parameter only when you want to create a new project, it can create multiple projects just you need to provide project names in csv file)
####  Process
     - Every process has its separate script in the bin folder.
     CopySetupScript :- It copies setup file in the output directory.
        Input: "${params.output_dir}" 
        Output: stdout 
     QC:- It takes QC of sample from basespace.   
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv) 
        Output: stdout 
     CNV_FeV2:- It analyse CNV for FeV2 sample
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *
     CNV_Indiegene:- 
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *
     DNA_fusion:-
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *_fusions, *intersected.bam, *intersected.bam.bai
     Hotspot
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *_alt_pipeline.vcf, *_Hotspot_V2.xlsx"
     Gene_Coverage
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *
## Process to run Nextflow NGSpipline
 #### Create CSV file
    "nf_MANIFEST.csv" 
    Please be careful when providing sample ids
    You just have to fill columns : Test_Name,Sample_Type,Capturing_Kit,Project_name,file_name (file_name is sample ids)
    Example:
    File Name: 1. WLVAR-B-D-GE-Nextflow-Test-S1_S1_L001_R1_001.fastq.gz (Already Renamed)
                  Sample Name will be : WLVAR-B-D-GE-Nextflow-Test-S1
               2. XAVAB_B1B2_D_L2_SE8_Nextflow_Test_R1.fastq.gz (Not Renamed)
                  Sample Name will be : XAVAB_B1B2_D_L2_SE8_Nextflow_Test
    - Test_Name,Sample_Type,Capturing_Kit column values are casesensitive
      1. Test_Name:- INDIEGENE, TARGET_FIRST, ABSOLUTE, SE8, ST8, CT (capital letter) etc
      2. Sample_Type:- DNA
      3. Capturing_Kit:- GE,CE,SE8,FEV2F2both
      Note- Use nf_manifest_maker.py file to create csv file if you do not want to create manually then Provide Project name and recheck sample name.
  #### Run script from terminal
     Run the script: 
     
     ```nextflow run Path/project_names_using_csv_file_ngs3_nextflow.nf --input_dir path/input_folder --sample_file path/test_ngs3_nextflow_Copy.csv --output_dir path/output_folder``` 
                       or
     When you have new project names in csv file:
     
    ``` nextflow run Path/project_names_using_csv_file_ngs3_nextflow.nf --input_dir path/input_folder --sample_file path/test_ngs3_nextflow_Copy.csv --output_dir path/output_folder --project new ```
   
  #### Steps for running nextflow script: https://docs.google.com/document/d/18IB0OyzrwdjB-TRqhlxHC4fQSoJ3cr750b5wpTMfFBs/edit?tab=t.0

  **Notes:** 
  1.Annotation and CGI are not included in this process. 
  2.Run Upstream and Downstream separately.
  
  




    
    

     
    
    

    
