# Nextflow_NGS3Pipeline 
## Aim:- Implementation of NGS3Pipeline in Nextflow 
## Overview 
The Nextflow NGS3Pipeline automates renaming, uploading, and analysis of NGS data using Nextflow. It takes FASTQ files and a sample CSV as input and processes them through multiple steps like renaming, project creation, basespace upload, basespace analysis and downstream analyses (e.g., CNV, QC, fusion, gene coverage). The workflow is structured around parameter definitions, individual processes, and a workflow definition.
## Requirements: 
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
     - For downstream processes, the scripts are the same as the previous ones, but you need to change the path in each script of the downstream for now but I will resolve this ASAP.
     Renaming 
        Input: "${params.input_dir}" "${params.sample_file}" "output.csv" 
        Output: "output.csv" 
     create_project
         Input: "output.csv"
         output: "created_proj.csv"
     extract_and_upload_samples 
        Input: "created_proj.csv" 
        Output: "new_file_test.csv" 
     preprocessing_for_launch  
        Input: "new_file_test.csv" 
        Output: "test_file.csv" 
     Target_first   
        Input: "test_file.csv" 
        Output: stdout 
     Indiegene_GE_Som
        Input: "test_file.csv"
        Output: stdout
     Indiegene_GE_germ
        Input: "test_file.csv"
        Output: stdout
     Indiegene_CE_som
        Input: "test_file.csv"
        Output: stdout
     Indiegene_CE_germ
        Input: "test_file.csv"
        Output: stdout
     SE8_som
        Input: "test_file.csv"
        Output: stdout
     SE8_germ
        Input: "test_file.csv"
        Output: stdout
     CDS
        Input: "test_file.csv"
        Output: stdout
     RNA_CT
        Input: "test_file.csv"
        Output: stdout
     RNA_SE8
        Input: "test_file.csv"
        Output: stdout
     Indiegene_CEFu
        Input: "test_file.csv"
        Output: stdout
     QC
        Input: Output directory, "test_file.csv"
        Output: stdout
     CNV
        Input: Output directory, "test_file.csv"
        oytput: "*"
     DNA_fusion
        Input:Output directory, "test_file.csv"
        Output: "*_fusions", "*intersected.bam", "*intersected.bam.bai"
     Hotspot
        Input:Output directory, "test_file.csv"
        Output: "*_alt_pipeline.vcf", "*_Hotspot_V2.xlsx"
     Gene_Coverage
        Input: Output directory, "test_file.csv"
        Output: "*"
## Process to run Nextflow NGSpipline
 #### Create CSV file
    test_ngs3_nextflow_Copy.csv 
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
      Note- Use test_file_for_nextflow.py file to create csv file if you do not want to create manually then Provide Project name and recheck sample name.
  #### Run script from terminal
     Run the script: nextflow run Path/project_names_using_csv_file_ngs3_nextflow.nf --input_dir path/input_folder --sample_file path/test_ngs3_nextflow_Copy.csv --output_dir path/output_folder 
                       or
     When you have new project names in csv file: nextflow run Path/project_names_using_csv_file_ngs3_nextflow.nf --input_dir path/input_folder --sample_file path/test_ngs3_nextflow_Copy.csv --output_dir path/output_folder --project new 
   
  #### Steps for running nextflow script: https://docs.google.com/document/d/18IB0OyzrwdjB-TRqhlxHC4fQSoJ3cr750b5wpTMfFBs/edit?tab=t.0

  **Notes:** 
  1.Annotation and CGI are not included in this process. 
  
  2.Run Upstream and Downstream separately.
  
  




    
    

     
    
    

    
