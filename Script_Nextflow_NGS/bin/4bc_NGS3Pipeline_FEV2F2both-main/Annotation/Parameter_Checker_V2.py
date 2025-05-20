# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 14:04:45 2023

@author: Prabir
"""

import subprocess
import time
from tqdm import tqdm
from colorama import init, Fore
import sys

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode().strip()

def check_data(data, previous_data):
    if previous_data is None:
        return False
    return data.strip('"') == previous_data.strip('"')

#def check_data(data, previous_data):
#    if previous_data is None or data is None:
#        return False
#    return data.strip('"') == previous_data.strip('"')


def print_right_symbol(message):
    print(Fore.GREEN + f"\033[1m\u2713 {message}\033[0m")

def print_cross_symbol(message):
    print(Fore.RED + f"\033[1m\u2717 {message}\033[0m")

def main():
    #analysis_name = "4th_Jan_24_W-180_T1_SOMATIC_DNA_FEV2F2both"#"07_Aug_23_W-151_Target_First_FEV2F2both"#"07_Aug_23_W-151_Target_First_FEV2F2both#"30_Jul_23_W-150_Target_First_plus_PDL1_FEV2F2both"#"30th_July_23_W-150_EMQN_TI_SOMATIC_DNA_CE"
    analysis_name = sys.argv[1]
    previous_vc_type = "1"
    
    #elif "FEV2F2BOTH" in analysis_name.upper():
    #    previous_target_bed_id = "TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed"
    #previous_target_bed_id = "sorted_TarGT_First_hg19.bed"
    previous_vc_type_blood = "0"
    sv_check = "1"
    vc_af_call_threshold = "5"
    vc_filterd_threshold = "10"

    if "germline" in analysis_name.lower():
        if "GE" in analysis_name.upper():
            previous_target_bed_id = "GERMLINE_Panel_163_GRCh37_13_Mar_23.bed"
        commands = [
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.vc-type --name {analysis_name}',
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.target_bed_id --name {analysis_name} | awk \'NR == 4 {{print $2}}\'',
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.sv_checkbox --name {analysis_name}',
        ]
        for command in tqdm(commands, desc="DRAGEN Parameter Validating", ncols=100):
            data = run_command(command)

            if "vc-type" in command:
                parameter_name = "vc-type"
            elif "target_bed_id" in command:
                parameter_name = "target_bed_id"
            elif "sv_checkbox" in command:
                parameter_name = "sv_checkbox"
        
            if "_germline_" in analysis_name.lower():
                if check_data(data, previous_vc_type_blood if "vc-type" in command else
                                  previous_target_bed_id if "target_bed_id" in command else
                                  sv_check if "sv_checkbox" in command else None):
                    print_right_symbol(f"{parameter_name} Checked: {data}")
                else:
                    print_cross_symbol(f"{parameter_name} Not Matched: {data}")

    elif "germline" not in analysis_name.lower():
        commands = [
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.vc-type --name {analysis_name}',
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.target_bed_id --name {analysis_name} | awk \'NR == 4 {{print $2}}\'',
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.sv_checkbox --name {analysis_name}',
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.af-filtering --name {analysis_name}',
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.vc-af-call-threshold --name {analysis_name}',
            f'/home/ubuntu/bs/bs get property appsession --property-name Input.vc-af-filter-threshold --name {analysis_name}'
        ]

        if "_Liquid_" in analysis_name:
            commands.append(f'bs get property appsession --property-name Input.liquid_tumor --name {analysis_name}')
            previous_vc_type_cf = "1"
            previous_target_bed_id_cf = "TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed"
            #if "GE" in analysis_name.upper():
                #previous_target_bed_id = "GERMLINE_Panel_163_GRCh37_13_Mar_23.bed"
            #elif "FEV2F2BOTH" in analysis_name.upper():
                #previous_target_bed_id = "TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed"
            vc_af_call_threshold_cf = "1"
            previous_liquid = "1"
            vc_filterd_threshold_cf = "5"
        for command in tqdm(commands, desc="DRAGEN Parameter Validating", ncols=100):
            data = run_command(command)

            if "vc-type" in command:
                parameter_name = "vc-type"
            elif "target_bed_id" in command:
                parameter_name = "target_bed_id"
            elif "sv_checkbox" in command:
                parameter_name = "sv_checkbox"
            elif "af-filtering" in command:
                parameter_name = "af-filtering"
            elif "vc-af-call-threshold" in command:
                parameter_name = "vc-af-call-threshold"
            elif "vc-af-filter-threshold" in command:
                parameter_name = "vc-af-filter-threshold"
            else:
                parameter_name = "liquid_tumor"

            if "_GE" in analysis_name.upper():
                previous_target_bed_id = "GERMLINE_Panel_163_GRCh37_13_Mar_23.bed"
            elif "_FEV2F2BOTH" in analysis_name.upper():
                previous_target_bed_id = "TarGT_First_v2_CDS_and_FEV2F2_GRCh37_30_Mar_23.bed"


            if "_Liquid_" in analysis_name:
                #print ("Liquid: ",analysis_name)
                #print (previous_target_bed_id)
                if check_data(data, previous_vc_type_cf if "vc-type" in command else
                                  previous_target_bed_id_cf if "target_bed_id" in command else
                                  previous_vc_type_cf if "sv_checkbox" in command else
                                  previous_vc_type_cf if "af-filtering" in command else
                                  previous_liquid if "liquid_tumor" in command else
                                  vc_af_call_threshold_cf if "vc-af-call-threshold" in command else
                                  vc_filterd_threshold_cf if "vc-af-filter-threshold" in command else None):
                    print_right_symbol(f"{parameter_name} Checked: {data}")
                else:
                    print_cross_symbol(f"{parameter_name} Not Matched: {data}")
            elif "_somatic_" in analysis_name.lower() and "_liquid_" not in analysis_name.lower() or "target_first_" in analysis_name.lower() and not "_liquid_" in analysis_name.lower() and not "_cfdna_" in analysis_name.lower():
                #print ("Non Liquid : ",analysis_name)
                #print (previous_target_bed_id)
                if check_data(data, previous_vc_type if "vc-type" in command else
                                  previous_target_bed_id if "target_bed_id" in command else
                                  previous_vc_type if "sv_checkbox" in command else
                                  previous_vc_type if "af-filtering" in command else
                                  vc_af_call_threshold if "vc-af-call-threshold" in command else
                                  vc_filterd_threshold if "vc-af-filter-threshold" in command else None):
                    print_right_symbol(f"{parameter_name} Checked: {data}")
                else:
                    print_cross_symbol(f"{parameter_name} Not Matched: {data}")
                    #print(f"\033[1mX {parameter_name} Not Checked: {data}\033[0m")

            #if "vc-type" in command:
            #    previous_vc_type = data
            #elif "target_bed_id" in command:
            #    previous_target_bed_id = data
if __name__ == "__main__":
    main()
