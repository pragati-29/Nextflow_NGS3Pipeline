input="list.txt"
mkdir annotation
while IFS= read -r line
do
mkdir "annotation/"${line}
echo "Starting ${line}"
#copying.hard-filtered.vcf from basespace and unzipping
echo "##########Starting copying.hard-filtered.vcf from basespace and unzipping#################"
#cp /home/ubuntu/basespace/Projects/Somatic_Patient_Samples_March_23/AppResults/${line}/Files/${line}.hard-filtered.vcf.gz ./
gunzip ${line}.hard-filtered.vcf.gz
echo "##########Ending copying.hard-filtered.vcf from basespace and unzipping#################"

#vcf to table
echo "##########Starting.hard-filtered.vcf conversion to tab#################"
python3 path/VCF-Simplify-master/VcfSimplify.py SimplifyVCF -toType table -inVCF "${line}.hard-filtered.vcf" -outFile "annotation/${line}/${line}.tab"

#Put dummy coloumn with constant value and create final tab file required in filter engine 
awk '$++NF=NR==1?"Overlaps_from_BAM":01' "annotation/"${line}/${line}.tab | cut -f 1-25 | sed 's/ /\t/g' > "annotation/"${line}/${line}_final.tab

echo "##########Ending.hard-filtered.vcf conversion to tab#################"
#annovar
echo "##########Starting annovar annotation#################"
perl path/Annotation_db/convert2annovar.pl -format vcf4old "${line}.hard-filtered.vcf" > "annotation/${line}/${line}.avinput"
perl path/Annotation_db/table_annovar.pl "annotation/${line}/${line}.avinput" path/Annotation_db/humandb/ -buildver hg19 -out "annotation/${line}/${line}_out" -remove -protocol ensGene,avsnp150,clinvar_20190305,intervar_20170202,intervar_20180118,esp6500siv2_all,exac03,gnomad211_exome,1000g2015aug_all,1000g2015aug_SAS,cadd13gt20,dbnsfp35a,dbscsnv11,dbnsfp31a_interpro -operation g,f,f,f,f,f,f,f,f,f,f,f,f,f -nastring .
echo "##########Ending annovar annotation#################"
#preparing config file
echo "##########Starting cancervar annotation#################"
perl path/4bc_NGS3Pipeline_FEV2F2both/Annotation/config.pl "annotation/"${line}/${line}
#running cancervar
python3 path/Annotation_db/CancerVar.py -c config.ini
echo "##########Ending cancervar annotation#################"
rm config.ini
done < "$input"
echo "################## ALL FILES ARE DONE ###########################"
