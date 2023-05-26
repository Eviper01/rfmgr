import sys
import os
import glob
from FileParsing import ParseReference

def OpenReference(file):
    try:
        with open(file, "r") as refFile:
            refData = refFile.read()
            ParseReference(refData, file)
    except FileNotFoundError:
        print("Invalid File Name:{Name} File not Found".format(Name=sys.argv[2]))

def QuickAdd(directory):
    list_of_files = glob.glob('{dir}/*'.format(dir=directory)) # * means all if need specific format then *
    latest_file = max(list_of_files, key=os.path.getctime)
    OpenReference(latest_file)

def AddAll(directory):
    list_of_files = glob.glob('{dir}/*'.format(dir=directory)) # * means all if need specific format then *
    for file in list_of_files:
        OpenReference(file)



if __name__ == "__main__":
    command = sys.argv[1]
    if command in ["import", "add"]:
        if len(sys.argv[2:]) == 0:
            print("No files specified to import")
        for file in sys.argv[2:]:
                OpenReference(file)
    if command in ["import-latest", "quickadd"]:
        try: 
            QuickAdd(sys.argv[2])
        except IndexError:
            print("Please specify a directory to import from")
    if command in ["import-all", "addall"]:
        AddAll(sys.argv[2])
