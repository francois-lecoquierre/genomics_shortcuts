
import tkinter as tk
from tkinter import *
from tkinter import ttk
import urllib3
from bs4 import BeautifulSoup
import os
import sys
import pandas as pd

# This script takes a BED file as an argument, iterates through each line and opens the IGV URL for each variant.

def get_bed_argument():
    """ args required : bed_file"""
    if not len(sys.argv) == 2:
        print("BED file needed as argument")
        exit()

    if not sys.argv[1].endswith(".bed"):
        print("BED file needed as argument")
        exit()
    bed_file = os.path.abspath(sys.argv[1])
    return bed_file


def parse_bed_file(file):
    # Check if file has header or not : if field 2 and field 3 are integers, then no header
    with open(file, 'r') as f:
        first_line = f.readline().strip()
        if first_line.startswith("#"):
            has_header = True
        else:
            has_header = False
    # Parse with pandas
    if has_header:
        # Parse with header
        df = pd.read_csv(file, sep="\t", header=0)
        # Change the three first columns to "chr", "start", "end"
        df.columns = ["chr", "start", "end"] + list(df.columns[3:])
    else:
        # Parse without header
        df = pd.read_csv(file, sep="\t", header=None)
        # Change the three first columns to "chr", "start", "end"
        df.columns = ["chr", "start", "end"] + [f"col{i}" for i in range(3, len(df.columns))]
    # Add empty classification column
    df["classification"] = ""
    # Return list of dicts
    output = df.to_dict(orient='records')
    return output



def igv_url_from_variant(variant):
    """ variant is a list extracted from the bed file"""
    print(variant)
    chr = variant["chr"]
    chr = chr.replace("chr", "")  # Remove 'chr' prefix if present
    start = variant["start"]
    end = variant["end"]
    url = f"http://localhost:60151/goto?locus={chr}:{start}-{end}"
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

        """ first frame : info """ # this frame contains the variant info that is displayed in the main window
        self.frame_info = Frame(self.master)
        self.frame_info.columnconfigure(0, weight=1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.grid(sticky="NSWE")
        # variant label
        self.variant_label = tk.Label(self.frame_info, text="Variant :")
        self.variant_label.pack()
        # size label
        self.size_label = tk.Label(self.frame_info, text="Size :")
        self.size_label.pack()
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
        button_forward.grid(row=1, column=len(buttons_colors) + 2)
        button_stats = Button(buttons_panel, text='Export results', command=lambda:self.stats())
        button_stats.grid(row=1, column=len(buttons_colors) + 3)
        grid_pos = 1
        for button_text, button_color in buttons_colors.items():
            grid_pos += 1
            btn = tk.Button(buttons_panel, text=button_text)
            btn.config(command= lambda t=button_text, btn = btn: self.custom_button_click(t))
            btn.grid(row=1, column=grid_pos)
            btn.config(background=button_color)
            btn.config(foreground="black")

    def update_info_field(self):
        self.master.title('Variant : ' + str(variant_number + 1) + "/" + str(len(variants)))
        variant = variants[variant_number]
        self.variant_label.config(text="Variant : " + str(variant["chr"]) + ":" + str(variant["start"]) + "-" + str(variant["end"]))
        self.size_label.config(text="Size : " + str(int(variant["end"]) - int(variant["start"])) + " bp")

        # Display the variant
        self.warning.set("Variant " + str(variant_number + 1) + " selected")
        self.warning.set("")

    def open_variant(self):
        global variant_number
        url = igv_url_from_variant(variants[variant_number])
        print(url)
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        BeautifulSoup(response.data)

    def custom_button_click(self, text):
        global variant_number
        print("Variant " + str(variant_number + 1) + " | Button called : " + str(text))
        variants[variant_number]["classification"] = text
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
        # Export the variants to a file
        classif_categories = buttons_colors.keys()
        print("Exporting variants to files...")
        for classification in classif_categories:
            export_filename = classification + "_variants.tsv"
            with open(export_filename, 'w') as f:
                # Create a dataframe for the variants of this classification
                df = pd.DataFrame([v for v in variants if v['classification'] == classification])
                # Save the dataframe to a tsv file if not empty
                if not df.empty:
                    df.to_csv(f, sep="\t", index=False)
                    print(f"Saved {len(df)} variants to {export_filename}")
        print("Export completed.")


# bed_file = "../bed_of_all_parents_canvas.bed"

bed_file = get_bed_argument()

# buttons_list = ["True positive", "?", "Other", "False positive"]
# we try a dict with the buttons and their colors
buttons_colors = {
    "True positive": "#2ecc71",
    "False positive": "#ec7063",
    "Other": "#f4d03f",
    "?": "#2980b9"
}

variants = parse_bed_file(bed_file) # Format 
variant_number = 0

app = MainWindow(tk.Tk())
app.mainloop()


