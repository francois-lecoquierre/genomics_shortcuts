
import tkinter as tk
from tkinter import *
from tkinter import ttk
import urllib3
from bs4 import BeautifulSoup
import os


def get_vcf_argument():
    """ args required : vcf_file"""
    if not len(sys.argv) == 2:
        print("VCF file needed as argument")
        exit()

    if not sys.argv[1].endswith(".vcf"):
        print("VCF file needed as argument")
        exit()
    vcf_file = os.path.abspath(sys.argv[1])
    return vcf_file


def parse_vcf_file(file):
    variants = [[line.rstrip('\n').split("\t"), ""] for line in open(file) if not line.startswith("#")]
    return variants


def get_header(file):
    header = [line for line in open(file) if line.startswith("#")]
    return(header)


def igv_url_from_variant(variant):
    """ variant is a list extracted from the vcf file"""
    if len(variant) > 1:
        if variant[0].startswith("chr"):
            chr = str(variant[0])
        else:
            chr = "chr" + str(variant[0])
        pos = str(variant[1])
        url = "http://localhost:60151/goto?locus=" + chr + ":" + pos
        return(url)


class MainWindow(ttk.Frame):
    """ Main window class """
    global variant_number

    def __init__(self, mainframe):
        """ Initialize the main Frame """
        ttk.Frame.__init__(self, master=mainframe)
        self.master.attributes("-topmost", True)
        self.master.geometry('800x90')  # size of the main window
        self.master.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        self.master.columnconfigure(0, weight=1)
        self.open_variant()

        """ first frame : info """
        self.frame_info = Frame(self.master)
        self.frame_info.columnconfigure(0, weight=1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.grid(sticky="NSWE")
        # display ref allele
        self.ref_allele = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.ref_allele).pack()
        # display alt allele
        self.alt_allele = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.alt_allele).pack()
        # display warning field
        self.warning = tk.StringVar()
        tk.Label(self.frame_info, textvariable=self.warning).pack()
        # populate allele fields
        self.update_info_field()

        """ second frame : buttons """
        buttons_panel = Frame(self.master)
        buttons_panel.grid(row=1)
        button_backward = Button(buttons_panel, text='<', command=lambda:self.backward())
        button_backward.grid(row=1, column=1)
        button_forward = Button(buttons_panel, text='>', command=lambda:self.forward())
        button_forward.grid(row=1, column=len(buttons_list) + 2)
        button_stats = Button(buttons_panel, text='Export results', command=lambda:self.stats())
        button_stats.grid(row=1, column=len(buttons_list) + 3)
        grid_pos = 1
        for button_text in buttons_list:
            grid_pos += 1
            btn = tk.Button(buttons_panel, text=button_text)
            btn.config(command= lambda t=button_text, btn = btn: self.custom_button_click(t))
            btn.grid(row=1, column=grid_pos)
            if button_text == "True positive":
                btn.config(background="#2ecc71")
            if button_text == "False positive":
                btn.config(background="#ec7063")
            if button_text == "Other":
                btn.config(background="#f4d03f")
            if button_text == "?":
                btn.config(background="#2980b9")

    def update_info_field(self):
        self.master.title('Variant : ' + str(variant_number + 1) + "/" + str(len(variants)))
        self.ref_allele.set("Ref : " + variants[variant_number][0][3])
        self.alt_allele.set("Alt : " + variants[variant_number][0][4])
        self.warning.set("")

    def open_variant(self):
        global variant_number
        url = igv_url_from_variant(variants[variant_number][0])
        print(url)
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        BeautifulSoup(response.data)

    def custom_button_click(self, text):
        global variant_number
        print("Variant " + str(variant_number + 1) + " | Button called : " + str(text))
        variants[variant_number][1] = text
        self.forward()

    def forward(self):
        global variant_number
        if variant_number + 1 == len(variants):
            self.warning.set("Last variant !")
        else:
            variant_number += 1
            self.update_info_field()
            self.open_variant()

    def backward(self):
        global variant_number
        if variant_number == 0:
            self.warning.set("First variant !")
        else:
            variant_number -= 1
            self.update_info_field()
            self.open_variant()

    def stats(self):
        classif_categories = list(filter(None, list(set([classificaiton for variant, classificaiton in variants]))))
        header = get_header(vcf_file)
        for classification in classif_categories:
            export_filename = os.path.splitext(vcf_file)[0] + '.' + str(classification.replace(" ", "_").replace("?", "Unknown")) + '.vcf'
            variants_to_export = [variant for variant, classif in variants if classif == classification]
            f = open(export_filename, "w+")
            for line in header:
                f.write(str(line))
            for line in variants_to_export:
                f.write("\t".join([str(i) for i in line]) + "\n")
            f.close()
            print("Exported : " + str(export_filename))
        self.warning.set("Successfully exported " + str(len(classif_categories)) + " files.")


# vcf_file = "/home/adm-loc/Documents/Programmes/python/trio1.GATK.split.de_novo_candidate.filtered.no_losses.gq.indels.vcf"

vcf_file = get_vcf_argument()

buttons_list = ["True positive", "?", "Other", "False positive"]

variants = parse_vcf_file(vcf_file)
variant_number = 0

app = MainWindow(tk.Tk())
app.mainloop()


