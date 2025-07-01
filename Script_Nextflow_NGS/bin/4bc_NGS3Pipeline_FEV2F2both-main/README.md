# NGS3Pipeline_FEV2F2both
FASTQ files are download from aws and initiate the downstream analysis.[FEV2F2both sample only]

# Project Pipeline Notice

**Important:** Before running the pipeline, please follow these instructions carefully to set up the necessary paths. As this pipeline is currently under development, manual path configuration is required. However, this path setup is a one-time task. Once configured, you won't need to change it every time you run the pipeline.

## Instructions

1. Open each and every file in the repository and locate the path configuration sections.
2. Update the paths according to your local environment. These path configurations are necessary for the pipeline to function correctly.

## Recommendations

- It is recommended to paste the pipeline's necessary data into your program folder.
- The `NGS3Pipeline_FEV2F2both.py` file should be placed in your local directory where you intend to run the sample.

**Attention:** Before executing the pipeline, ensure that you have created the required CSV file. This CSV file is essential for the pipeline's proper functioning.

By following these instructions, you'll be able to successfully set up and run the pipeline in your local environment.
# Running the Script

To run the pipeline script, follow the steps below:

1. Make sure you have Python 3 installed on your system.

2. Open a terminal or command prompt.

3. Navigate to the directory where the script `NGS3Pipeline_FEV2F2both.py` is located.

4. Run the script using the following command:

```bash
python3 NGS3Pipeline_FEV2F2both.py argument1 argument2

```

Replace argument1 with your AWS folder name and argument2 with your batch ID or batch name.
For example, if your AWS folder name is "my_aws_folder" and your batch ID is "batch123", the command would be:

```bash
python3 NGS3Pipeline_FEV2F2both.py my_aws_folder batch123
```

Make sure you have configured the paths as instructed in the previous section before running the script.

If you encounter any issues or need further assistance, please don't hesitate to reach out.


This section provides clear instructions on how to run the script with arguments and provides an example for better understanding. Make sure to adapt the instructions to match your script's filename and the specific arguments it expects.

Here is the workflow of NGS3pipiline -

![NGS2Pipeline drawio (1)](https://github.com/prabir4bc/NGS3Pipeline_FEV2F2both/assets/110020197/30bffe34-3c3d-4773-803d-43638bee96fd)

Please feel free to contact us if you encounter any issues or require further assistance.
