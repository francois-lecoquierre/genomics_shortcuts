# this script works best when launched via a keyboard shortcut
# you need to select with your mouse the vcf fields of a variant (in a more or grep command for instance), then run the script
# the script parses the selected data, to get the first and second fields (chr and pos), and generates the igv URL to open

import tkinter
import urllib3
from bs4 import BeautifulSoup

root = tkinter.Tk()
clipboard = root.selection_get(selection="PRIMARY")
print(clipboard)

clip_list = clipboard.split("\t")
print(clip_list)

if len(clip_list) > 1:
    if clip_list[0].startswith("chr"):
        chr = str(clip_list[0])
    else:
    	chr = "chr" + str(clip_list[0])
    pos = str(clip_list[1])
    url = "http://localhost:60151/goto?locus=" + chr + ":" + pos

    print(url)
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data)




