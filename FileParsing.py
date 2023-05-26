import glob
import importlib
import sys
sys.path.append(__file__+'/../Parsers/')





def LoadParsers():
    parsers = glob.glob(__file__+'/../Parsers/*') # * means all if need specific format then *
    return [parser.split("\\")[-1].split(".")[0] for parser in parsers] 

def ParseReference(text, filename):
    extension = filename.split(".")[-1]
    parsers = LoadParsers()
    print(parsers)
    if extension in parsers:
        parser = importlib.import_module(extension)
        parser.parse("test")