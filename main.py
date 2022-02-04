import os

def import_test(module_install, module_script):
    try:
     exec("import "+module_script)
    except ModuleNotFoundError:
     print("Installing required module:"+module_install)
     os.system("pip install "+module_install)

list_of_modules_for_install = ["beautifulsoup4", "pandas", "steam", "patool", "google"]

list_of_modules_for_script = ["bs4", "pandas", "steam", "patoolib", "google"]

for n in range(0, len(list_of_modules_for_install)):
 import_test(list_of_modules_for_install[n], list_of_modules_for_script[n])

