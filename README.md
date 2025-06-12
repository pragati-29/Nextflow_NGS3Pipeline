# Nextflow_NGS3Pipeline 
## Aim:- Implementation of NGS3Pipeline in Nextflow 
## Overview 
This Nextflow pipeline is designed for comprehensive downstream analysis of next-generation sequencing (NGS) data. It supports the execution of multiple processes CNV, gene coverage, hotspot, QC, and DNA fusion. You will need to provide a csv file where you will keep all the information regarding samples and in output folder you will get subfolders for each process (CNV, Hotspot, QC, DNA Fusion, Gene coverage).
## Steps to run pipeline
  1. Install:
      * nextflow
      * python
      * bs
      * all required tools for downstream process
          * Mosdepth
          * Freebayes
          * sambamba
          * samtools
          * fuseq
          * control freec
          * IGV

  > [!NOTE]
  > You can use nf_ngs3pipeline_env.yml file for installation of these tools.
  >
  > ```bash
  > conda env create -f /path/to/nf_ngs3pipeline_env.yml
  > ```

  2. Clone github repository
     ```bash
     git clone --branch Downstream https://github.com/pragati-29/Nextflow_NGS3Pipeline.git
     ```
  4. Edit setup.sh file from bin folder of repository
  5. Create csv file manually or from upstream output process (nf_final_MENIFEST.csv)
  6. Do basemount in output folder and keep csv file there.
  7. Run the command for nextflow pipeline

      ```bash
     nextflow run Path/to/NGSPipeline_Nextflow_Segregated_Test.nf \
      --input_dir path/to/input_folder \
      --sample_file path/to/nf_final_MANIFEST.csv \
      --output_dir path/output_folder
      ```

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
  * Subfolders for each downstream process that contain their output data
## Sections of the Script:
#### Parameter Definitions

| Parameter           | Definition                                                                                  |
|---------------------|----------------------------------------------------------------------------------------------|
| `params.input_dir`  | Input directory having FASTQ files                                                           |
| `params.sample_file`| `nf_final_MANIFEST.csv` file                                                                 |
| `params.output_dir` | Output directory MUST have `basemount` and `nf_final_MANIFEST.csv` file                      |
| `params.project`    | Use this parameter only when you want to create a new project. It can create multiple projects—just provide project names in the CSV file |

#### Process

     - Every process has its separate script in the bin folder.

     CopySetupScript :- It copies setup file in the output directory.
        Input: "${params.output_dir}" 
        Output: stdout 
     QC:- It takes QC of sample from basespace.   
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv) 
        Output: stdout 
        script: bs command
     CNV_FeV2:- It analyse CNV for FeV2 sample
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *
        Script: CNV_somatic_FeV2.sh
        Tool: control freec 
     CNV_Indiegene:- 
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *
        Script: cnv_annotation_somatic_CE.sh
        Tool: control freec
     DNA_fusion:-
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *_fusions, *intersected.bam, *intersected.bam.bai
        Script: FuSeq_BAM_FUS_auto.sh
        Tool: fuseq
     Hotspot
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *_alt_pipeline.vcf, *_Hotspot_V2.xlsx"
        Script: Alternate_VariantCaller_to_Hotspot_V2_09_Apr_24.py
        Tool: freebayes
     Gene_Coverage
        Input: params.output_dir, params.sample_file (sample file - nf_final_MANIFEST.csv)
        Output: *
        Script: Gene_Coverage_via_Mosdepth_V2.py
        Tool: mosdepth

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

- ``Test_Name``,``Sample_Type``,``Capturing_Kit`` column values are **casesensitive**
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
