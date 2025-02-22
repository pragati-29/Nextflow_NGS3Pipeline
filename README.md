# Nextflow_NGS3Pipelin 
## Aim:- Implementation of NGS3Pipeline in Nextflow 
## Overview 
This script defines a Nextflow pipeline used for processing, uploading and analysis of sequencing data. It handles renaming files and uploading datasets to BaseSpace projects based on specific sample naming conventions and their analysis. The workflow is structured around parameter definitions, individual processes, and a workflow definition. 
## Requirements: 
  * Nextflow
  * Python
    * subprocess
    * pandas
    * re
    * csv
    * datetime 
  * Basespace Illumina access
  * Java (For Nextflow installation)
### Nextflow installation
  * Install SDKMAN:
      curl -s https://get.sdkman.io | bash
  * Install JAVA:
      sdk install java 17.0.10-tem
  * Install Nextflow:
      curl -s https://get.nextflow.io | bash
  * Make Nextflow executable:
      chmod +x nextflow
   
### Input:
  * Folder of fastq files (All types)
  * csv file
  * Output Folder
### Output:
  * Renaming of samples for uploading in basespace
  * Uploaded samples in basespace projects
  * Analysis of samples
### Sections of the Script:
#### Parameter Definitions
    params.input_dir 
    params.sample_file 
    params.output_dir 
####  Process
     Renaming 
        Input: "${params.input_dir}" "${params.sample_file}" "output.csv" 
        Output: "output.csv" 
     extract_and_upload_samples 
        Input: "output.csv" 
        Output: "new_file_test.csv" 
     preprocessing_for_launch  
        Input: "new_file_test.csv" 
        Output: "test_file.csv" 
     bs_launch   
        Input: "test_file.csv" 
        Output: stdout 
### Process to run Nextflow NGSpipline
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
      1. Test_Name:- INDIEGENE, TARGET_FIRST, ABSOLUTE (capital letter)
      2. Sample_Type:- DNA
      3. Capturing_Kit:- GE,CE,SE8,FEV2F2both
  #### Run script from terminal
     nextflow run Path/project_names_using_csv_file_ngs3_nextflow.nf --input_dir path/input_folder --sample_file path/test_ngs3_nextflow_Copy.csv --output_dir path/output_folder
  ### Note: RNA (CT and ST8) and Fe are not included yet




    
    

     
    
    

    
