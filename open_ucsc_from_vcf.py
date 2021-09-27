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
