import os

def read_config():
    chrome_file = "chrome.conf"
    if os.path.isfile(chrome_file):
       path_file = open(chrome_file, "r")
       path = path_file.read().rstrip('\n')
       path_file.close()
       return path
    else:
       return 0

