cd {{location}}

bs upload dataset --project={{pid}} *R1_001.fastq.gz *R2_001.fastq.gz
sleep 20m

samples=({{samplenames}}) #list of samples
bsids=()  
other_samples=() 
not_fetched=()  

for i in "${samples[@]}"; do
  echo "Processing sample: $i"
  attempt_count=0  
  
  while true; do
    bsid=$(bs get biosample -n "$i" –terse | grep "Id" | head -1 | grep -Eo '[0-9]{1,}')
    
    if [ -n "$bsid" ]; then
      bsids+=("$bsid")
      other_samples+=("$bsid")  
      break  
    else
      echo "No ID found for sample: $i. Retrying after 3 minutes."
      sleep 280
      ((attempt_count++))  # Increment attempt counter
      
      if [ $attempt_count -eq 5 ]; then
        echo "Moving to next sample for search."
        not_fetched+=("$i") 
        break 
      fi
    fi
    
  done
done
echo "All fetched sample IDs: ${bsids[@]}"
echo "Sample IDs not fetched after 5 attempts: ${not_fetched[@]}"

printf -v joined '%s,' "${bsids[@]}"
bsids=${joined%,}
echo $bsids

{{bscmd}}

:'
bs upload dataset --project={{pid}} *R1_001.fastq.gz *R2_001.fastq.gz

sleep 45m

samples=({{samplenames}}) #list of samples

for i in ${samples[@]};  do
echo $i;
bsid=`bs get biosample -n $i â€“terse | grep "Id" | head -1 | grep -Eo '[0-9]{1,}'`;
bsids+=($bsid)
done
printf -v joined '%s,' "${bsids[@]}"
bsids=${joined%,}
echo $bsids

{{bscmd}}
'
echo "########################"
echo "Dragen Launched"
echo "########################"
perl path/fastqc_v0.11.9/FastQC/fastqc *.gz
echo "########################"
echo "FastQC completed"
echo "########################"

cp path/Renaming-Downstream.py ./
python3 Renaming-Downstream.py

my_var="{{app-session-name}}"
dirpath="{{location}}"
projectname="{{project_name}}"

mkdir annotation
mkdir {{location}}/CNV
mkdir {{location}}/Gene-Coverage
mkdir {{location}}/Panel
mkdir {{location}}/Hotspot
mkdir {{location}}/CNV-Coverage
cd {{location}}/annotation
cp path/4bc_NGS3Pipeline_FEV2F2both/Annotation/anno_auto_mod.py {{location}}/annotation
chmod 777 anno_auto_mod.py
cp path/4bc_NGS3Pipeline_FEV2F2both/Annotation/qc_upd2.py {{location}}
chmod 777 qc_upd2.py
cd ..
cd {{location}}/Hotspot
cp path/4bc_NGS3Pipeline_FEV2F2both/Annotation/Alternate_VariantCaller_to_Hotspot_V2_09_Apr_24.py {{location}}/Hotspot
chmod 777 Alternate_VariantCaller_to_Hotspot_V2_09_Apr_24.py
cd ..
echo {{location}}
cd {{location}}/CNV-Coverage
cp path/4bc_NGS3Pipeline_FEV2F2both/dragen_output_covrage_file_based_CNV.py {{location}}/CNV-Coverage
cp path/4bc_NGS3Pipeline_FEV2F2both/TarGT_First_v2_FEV2F2both_cnv_coverage.bed {{location}}/CNV-Coverage
chmod 777 dragen_output_covrage_file_based_CNV.py
chmod 777 TarGT_First_v2_FEV2F2both_cnv_coverage.bed
cd ..
echo {{location}}
cd {{location}}/CNV
cp path/4bc_NGS3Pipeline_FEV2F2both/CNV/cnv_annotation_somatic.sh {{location}}/CNV
cp path/4bc_NGS3Pipeline_FEV2F2both/CNV/cnv_config_somatic.pl {{location}}/CNV
cd ..
cd {{location}}/Gene-Coverage
cp path/4bc_NGS3Pipeline_FEV2F2both/Gene-Coverage/Gene_Coverage_via_Mosdepth_V2.py {{location}}/Gene-Coverage
cp path/4bc_NGS3Pipeline_FEV2F2both/Gene-Coverage/Hori_Gen_Coverage.py {{location}}/Gene-Coverage
chmod 777 Hori_Gen_Coverage.py
chmod 777 Gene_Coverage_via_Mosdepth_V2.py
cd ..
cd {{location}}/annotation
python3 {{location}}/annotation/anno_auto_mod.py $my_var $dirpath $projectname

