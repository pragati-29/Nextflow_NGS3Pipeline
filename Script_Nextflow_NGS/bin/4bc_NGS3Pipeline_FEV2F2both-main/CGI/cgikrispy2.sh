#!/bin/bash

:'source /home/ubuntu/anaconda3/etc/profile.d/conda.sh

conda activate
'
cd {{location}}
export CGI_DATA={{cgi_data}}
export TRANSVAR_CFG=${CGI_DATA}/transvar.cfg
export TRANSVAR_DOWNLOAD_DIR=${CGI_DATA}/transvar

samples=({{samplenames}})
 
for line in ${samples[@]};
do
echo "Starting CGI analysis for  ${line}"
cgi -i ${line} -o ${line}_CGI

echo "Starting Comprssion of ${line}"
:'zip -r ${line}_CGI.zip ${line}_CGI'

sample_name=$(basename "${line}")
zip -r "${sample_name}_CGI.zip" "${sample_name}_CGI"

echo "Ending CGI analysis for ${line} and compressed the Results"
done



echo "################## ALL CGI RESULTS GENERATED ########################"


echo "   "

echo "################## Initiating Renaming CGI output files #############"
for folder in */; do
    echo "Processing folder: $folder"
    cd "$folder"
    prefix="${folder%%.*}"
    for file in *; do
        new_filename="${prefix}_$file"
        echo "Renaming $file to $new_filename"
        mv "$file" "$new_filename"
    done
    cd ..

done

echo "### Renaming completed ###"


