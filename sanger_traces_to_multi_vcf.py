# this script generates a multi vcf file from a list of ab1 files
# it uses the indigo script to align the ab1 files on the reference genome and call the variants
# requirements : indigo, bcftools, snpEff, easygui

import os
from easygui import *


def launch_indigo(indigo_script, ref_genome_gz, ab1_file, ltrim, rtrim, peak_percentage_to_call, output_folder):
    print("Launching Indigo on the following *******************************")
    print("Options ***")
    print("Script : " + indigo_script)
    print("Genome : " + ref_genome_gz)
    print("Ab1 file : " + ab1_file)
    print("Ltrim : " + str(ltrim))
    print("Rtrim : " + str(rtrim))
    print("Peak percentage to call : " + str(peak_percentage_to_call))
    print("Output folder : " + output_folder)
    print("*******************************************************************")

    ab1_file_no_folder = ab1_file.split("/")[-1]
    input_folder = "/".join(ab1_file.split("/")[:-1]) + "/"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    """on lance la commande bash d'indigo"""
    options = str(ltrim) + " " + str(rtrim) + " " + str(peak_percentage_to_call)
    bashCommand = indigo_script + " " + input_folder + ab1_file_no_folder + " " + ref_genome_gz + " " + options + " " + output_folder + ab1_file_no_folder
    print(bashCommand)
    print("")
    os.system(bashCommand)

    # on retourne le nom du fichier bcf généré
    bcf_file = output_folder + ab1_file_no_folder + ".bcf"
    # on regarde si le fichier bcf a bien été généré
    if not os.path.exists(bcf_file):
        print("Indigo analysis failed to generate the bcf file")
        # on met un message easygui, soit l'usilisateur valide, soit il annule le processus
        msg = "Indigo analysis failed to generate the bcf file. Do you want to continue the process ?"
        title = "Indigo analysis failed on " + ab1_file_no_folder
        if ccbox(msg, title):
            print("User wants to continue the process")
        else:
            print("User wants to stop the process")
            exit()
        return None
    else:
        # on met le nom du sample dans le fichier bcf : création du fichier temporaire contenant le nom du sample, puis bcftools reheader
        sample_name = ab1_file_no_folder.split(".")[0]
        sample_name_file = "tempo.txt"
        with open(sample_name_file, 'w') as f:
            f.write(sample_name)
        renamed_bcf_file = output_folder + ab1_file_no_folder + "_renamed.bcf"
        bashCommand = "bcftools reheader -s " + sample_name_file + " " + bcf_file + " > " + renamed_bcf_file
        print(bashCommand)
        os.system(bashCommand)
        print("Generated bcf file : " + renamed_bcf_file)
        # indexation du fichier bcf
        bashCommand = "bcftools index " + renamed_bcf_file
        print(bashCommand)
        os.system(bashCommand)
        return renamed_bcf_file


def merge_bcf_files(files, output_name):
    """
    fusionne les fichiers bcf
    """
    # on crée un fichier temporaire contenant la liste des fichiers bcf à fusionner
    files_list = "tempo.txt"
    with open(files_list, 'w') as f:
        for file in files:
            f.write(file + "\n")
    # on fusionne les fichiers
    multi_vcf_file = output_name + ".vcf"
    bashCommand = "bcftools merge -l " + files_list + " -O v -o " + multi_vcf_file
    print(bashCommand)
    os.system(bashCommand)
    return multi_vcf_file


def bcf_to_vcf(file):
    bcf_file = file + ".bcf"
    vcf_file = file + ".vcf"
    """on lance la commande bash bcftools"""
    bashCommand = "bcftools view " + bcf_file + " > " + vcf_file
    print(bashCommand)
    os.system(bashCommand)


def annotate_vcf(file_without_extension):
    file_input = file_without_extension + ".vcf"
    file_output = file_without_extension + "_ann.vcf"
    bashCommand = "java -Xmx8g -jar /home/adm-loc/Documents/Programmes/snpeff/snpEff/snpEff.jar GRCh37.75 " + file_input + " > " + file_output
    print(bashCommand)
    os.system(bashCommand)





""" xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx """

# variables d'entrée
input_files = fileopenbox("Selection des fichiers", "Sélectionner les fichiers .ab1 à analyser", filetypes= "*.ab1", multiple=True, default=r"/home/adm-loc/Documents/Programmes/indigo/")
output_folder = diropenbox("Selection du dossier de sortie", "Sélectionner le dossier de sortie", default=r"/home/adm-loc/Documents/Programmes/indigo/")
tmp_folder = output_folder + "tmp/"
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)
output_prefix = enterbox("Entrez le préfixe du fichier de sortie", "Préfixe du fichier de sortie", "output")
output_multi_vcf = output_folder + "/" + output_prefix + "_multi.vcf"

# variables fixes
indigo = "/home/adm-loc/Documents/Programmes/indigo/indigo/indigo.sh"
genome_ref = "/media/adm-loc/DATA_1To2/genome/hg19.fa.gz"

files = []
for file in input_files:
    generated_file_prefix = output_folder + file.split("/")[-1]
    bcf_file = launch_indigo(indigo, genome_ref, file, 50, 50, 0.3, output_folder)
    if bcf_file:
        files.append(bcf_file)
    # bcf_to_vcf(generated_file_prefix)
    # annotate_vcf(generated_file_prefix)
    # vcf_to_xlsx(generated_file_prefix)
    # vcf_to_pdf(generated_file_prefix)
    # merge_pdf(generated_file_prefix)

multi_vcf_file = merge_bcf_files(files, output_multi_vcf)

if multi_vcf_file:
    print("Generated multi vcf file : " + multi_vcf_file)














