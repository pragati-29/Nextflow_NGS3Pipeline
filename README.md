# Nextflow_NGS3Pipelin 
## Aim:- Implementation of NGS3Pipeline in Nextflow 
## Overview 
This script defines a Nextflow pipeline used for processing and uploading sequencing data. It handles renaming files and uploading datasets to BaseSpace projects based on specific sample naming conventions. The workflow is structured around parameter definitions, individual processes, and a workflow definition. 
## Requirements: 
  * Nextflow
  * Python
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
  * Rename_combined.py file
  * Folder of fastq files (All types)
  * Project Ids for Germline, Somatic, and RNA
### Output:
  * Renaming of samples for uploading on basespace
  * Uploaded samples in basespace projects 
### Sections of the Script:
#### Parameter Definitions
    Parameters in Nextflow scripts provide configurable values that can be adjusted without modifying the core script logic.
    

    
