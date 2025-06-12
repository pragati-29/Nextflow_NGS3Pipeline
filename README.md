# Nextflow_NGS3Pipeline 
## Aim:- Implementation of NGS3Pipeline in Nextflow 
## Overview 
The Nextflow NGS3Pipeline automates renaming, uploading, and analysis of NGS data using Nextflow. It takes FASTQ files and a sample CSV as input and processes them through multiple steps like renaming, project creation, basespace upload, basespace analysis. The workflow is structured around parameter definitions, individual processes, and a workflow definition.
## Steps to run pipeline
  1. Install:
      * nextflow
      * python
      * Install bs command for upstream process
  > [!NOTE]
  > You can use nf_ngs3pipeline_env.yml file for installation of these tools.
  >
  > ```bash
  > conda env create -f /path/to/nf_ngs3pipeline_env.yml
  > ```

  2. Clone github repository
     ```bash
     git clone --branch Upstream https://github.com/pragati-29/Nextflow_NGS3Pipeline.git
     ```
  4. Edit setup.sh file from bin folder of repository and run it.
  6. Create csv file manually or from nf_manifest_maker.py script. keep nf_manifest_maker.py in fastq file (input_folder) directory.
  8. Run the command for nextflow pipeline

      ```bash
     nextflow run Path/to/NGSPipeline_Nextflow_Segregated_Test.nf \
      --input_dir path/to/input_folder \
      --sample_file path/to/nf_final_MANIFEST.csv \
      --output_dir path/output_folder
      ``` 
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
| Parameter           | Definition                                                                                  |
|---------------------|----------------------------------------------------------------------------------------------|
| `params.input_dir`  | Input directory having FASTQ files                                                           |
| `params.sample_file`| csv file (nf_manifest_maker.py file output )                                                                |
| `params.output_dir` | Output directory MUST have `basemount` and `nf_final_MANIFEST.csv` file                      |
| `params.project`    | Use this parameter only when you want to create a new project. It can create multiple projects—just provide project names in the CSV file |
####  Process
     - Every process has its separate script in the bin folder.
     Renaming 
        Input: "${params.input_dir}" "${params.sample_file}" "output.csv" 
        Output: "bs_compliant_sample_renamed.csv" 
        Script: Rename_combined.py
     create_project
         Input: "output.csv"
         output: "created_proj.csv"
         Script: Create_project.py
     extract_and_upload_samples 
        Input: "created_proj.csv" 
        Output: "preanalysis_details.csv"
        Script: bs_preanalysis.py
     preprocessing_for_launch  
        Input: "new_file_test.csv" 
        Output: "nf_final_MANIFEST.csv" 
        Script: preprocessing_for_launch.py
     Target_first   
        Input: "nf_final_MANIFEST.csv" 
        Output: stdout 
        Script: Target_First.py
     Indiegene_GE_Som
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: Indiegene_GE_som.py
     Indiegene_GE_germ
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: Indiegene_GE_germ.py
     Indiegene_CE_som
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: Indiegene_CE_som.py
     Indiegene_CE_germ
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: Indiegene_CE_germ.py
     SE8_som
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: SE8_som.py
     SE8_germ
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: SE8_germ.py
     CDS
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: CDS.py
     RNA_CT
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: RNA_CT.py
     RNA_SE8
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: RNA_ST8.py
     Indiegene_CEFu
        Input: "nf_final_MANIFEST.csv"
        Output: stdout
        Script: Indiegene_CEFu.py

## Process to run Nextflow NGSpipline

### Create CSV file

``"nf_final_MANIFEST.csv"``

**Please be careful when providing sample ids**

You just have to fill columns : ``Test_Name``,``Sample_Type``,``Capturing_Kit``,``Project_name``,``file_name`` (file_name is sample ids)

Example:
File Name: 1. WLVAR-B-D-GE-Nextflow-Test-S1_S1_L001_R1_001.fastq.gz (Already Renamed)
              Sample Name will be : WLVAR-B-D-GE-Nextflow-Test-S1
           2. XAVAB_B1B2_D_L2_SE8_Nextflow_Test_R1.fastq.gz (Not Renamed)
              Sample Name will be : XAVAB_B1B2_D_L2_SE8_Nextflow_Test

* ``Test_Name``,``Sample_Type``,``Capturing_Kit`` column values are **casesensitive**
  1. Test_Name:- INDIEGENE, TARGET_FIRST, ABSOLUTE, SE8, ST8, CT (capital letter) etc
  2. Sample_Type:- DNA
  3. Capturing_Kit:- GE,CE,SE8,FEV2F2both

> [!NOTE]
> Use ``nf_manifest_maker.py`` file to create csv file if you do not want to create manually then Provide Project name and recheck sample name.

### Run script from terminal

Run the script:

```bash
nextflow run Path/to/NGSPipeline_Nextflow_Segregated_Test.nf --input_dir path/to/input_folder --sample_file path/to/nf_final_MANIFEST.csv --output_dir path/output_folder
```

When you have new project names in csv file:

```bash
nextflow run Path/to/NGSPipeline_Nextflow_Segregated_Test.nf --input_dir path/to/input_folder --sample_file path/to/nf_final_MANIFEST.csv --output_dir path/output_folder --project new
```

  > [!NOTE]
  > 1.Annotation and CGI are not included in this process.
  >
  > 2.Run Upstream and Downstream separately.
