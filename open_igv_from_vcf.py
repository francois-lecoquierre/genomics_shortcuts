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
        url = "http://localhost:60151/goto?locus=" + str(clip_list[0]) + ":" + str(clip_list[1])
    else:
        url = "http://localhost:60151/goto?locus=chr" + str(clip_list[0]) + ":" + str(clip_list[1])

print(url)

http = urllib3.PoolManager()
response = http.request('GET', url)
soup = BeautifulSoup(response.data)


# urllib3.request.urlopen(url)



