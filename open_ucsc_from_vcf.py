# this script works best when launched via a keyboard shortcut
# you need to select with your mouse the vcf fields of a variant (in a more or grep command for instance), then run the script
# the script parses the selected data, to get the first and second fields (chr and pos), and generates the ucsc URL to open

import tkinter
import webbrowser


ucsc_user = "francois.leco"
ucsc_session = "hg38_evalutation_compexite"


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
    url = "http://genome-euro.ucsc.edu/cgi-bin/hgTracks?hgS_doOtherUser=submit&hgS_otherUserName=" + ucsc_user + "&hgS_otherUserSessionName=" + ucsc_session + "&position=" + chr + ":g." + pos

    print(url)
    webbrowser.open(url)
