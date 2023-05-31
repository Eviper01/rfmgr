import sys
import os
import glob
import pprint
import json
import importlib
import sys
sys.path.append(__file__+'/../Parsers/')

#Global Variables
db = None
tags = []
bib_file = None
ref_db = None



def LoadParsers():
    """Checks in the /Parsers/ Directory for the avalible {ext}.py Parsers"""
    parsers = glob.glob(__file__+'/../Parsers/*') # * means all if need specific format then *
    return [parser.split("\\")[-1].split(".")[0] for parser in parsers] 

def ParseReference(text, filename):
    """Passes the text in the ref file to the relvant parser returns in dictionary of key value pairs that have the same names and formatting as bibtex however 'ref' is used to denote the refernce identifier """
    extension = filename.split(".")[-1]
    parsers = LoadParsers()
    if extension in parsers:
        parser = importlib.import_module(extension)
        return parser.parse(text, filename)
    print("ParseRefernce: parser not found")
    return None


def BibTexExport(reference_object):
    template = """
    @article{{
    {InText},
    Author  =   {{{Authour}}},
    Title   =   {{{Title}}},
    Journal =   {{{Journal}}},
    Volume  =   {{{Volume}}},
    Number  =   {{{Number}}},
    Pages   =   {{{Pages}}},
    Year    =   {{{Year}}},
    DOI     =   {{{DOI}}} }}
    """
    formatted_reference = template.format(
    InText  = reference_object["InText"],
    Title   = reference_object["Title"],
    Authour = reference_object["Authour"],
    Journal = reference_object["Journal"],
    Volume  = reference_object["Volume"],
    Pages   = reference_object["Pages"],
    Year    = reference_object["Year"],
    DOI     = reference_object["DOI"],
    Number  = reference_object["Number"],
    )
    return formatted_reference
    
def WriteBibliography(text):
    with open(bib_file, "w") as file:
        file.write(text)




def LoadConfig():
    global db
    global tags
    global bib_file
    MissingConfig = False
    """Loads the config from the config.json file which is in the same directory as main.py"""
    try:
        with open(__file__+'/../config.json',"r") as file:
            config = json.load(file)
    except FileNotFoundError:
        print("config.json file not found, will create one instead")
        MissingConfig = True
    try:
        db = config['db']
    except KeyError:
        print('database pointer missing defaulting to', __file__+'/../db.json')
        db = __file__+'/../db.json'
    except UnboundLocalError:
        db = __file__+'/../db.json'
    try:
        tags = config['tags']
    except KeyError:
        print("Could not find any working tags")
        tags = []
    except UnboundLocalError:
        tags = []
    try:
        bib_file = config['bib_file']
    except KeyError:
        print("Could not find pointer to bib file:")
        print("defaulting to", __file__+'/../bibfile.bib')
        bib_file = __file__+'/../bibfile.bib'
    except UnboundLocalError:
        bib_file = __file__+'/../bibfile.bib' 
        print("bib file defaulting to", __file__+'/../bibfile.bib') 
    if MissingConfig:
        with open(__file__+'/../config.json',"w") as file:
            config = {
                        'db': db,
                        'tags': tags,
                        'bib_file': bib_file 
                    }
            file.write(json.dumps(config, indent = 4))

def SaveConfig():
    with open(__file__+'/../config.json',"w") as file:
        config = {
                    'db': db,
                    'tags': tags,
                    'bib_file': bib_file
                }
        file.write(json.dumps(config, indent = 4))

def LoadDatabase():
    try:
        with open (db,'r') as file:
            return json.loads(file.read()) 
    except FileNotFoundError:
        print("LoadDataBase: cannot find database file, will start a new one.")
        return {}

def WriteDatabase():
    with open (db,'w') as file: 
        file.write(json.dumps(ref_db, indent = 4))

def SaveReferences(references_list):
    global ref_db
    for reference in references_list:
        reference['tags'] = tags
        if reference['InText'] not in ref_db.keys():
            ref_db[reference['InText']] = reference
        else:
            print("SaveReferences: Warning: potential duplicate reference found")
            print("Trying to Save:")
            pp = pprint.PrettyPrinter(indent=4, width=200)
            print("Old Reference:")
            pp.pprint(ref_db[reference['InText']])
            print("New Reference:")
            pp.pprint(reference)
            #run something to handle duplicates
            handling = True
            while handling:
                action = input("'o' to overwrite, 'd' to discard new reference, 'n' to manually specify name: ")
                if action == 'o':
                    ref_db[reference['InText']] = reference
                    handling = False
                if action == 'd':
                    handling = False
                if action == 'n':
                    name = input("Specify name: ")
                    reference["InText"] = name
                    ref_db[name]= reference
                    handling = False
                if handling: 
                    print("Invalid option")


def OpenReference(file):
    """opens and parsers the specifed file """
    try:
        with open(file, "r") as refFile:
            refData = refFile.read()
            SaveReferences((ParseReference(refData, file)))
    except FileNotFoundError:
        print("OpenRefernce: Invalid File Name:{Name} File not Found".format(Name=sys.argv[2]))
    except UnicodeDecodeError:
        with open(file, "r", encoding="utf-8") as refFile:
            print("Open Reference: Warning: Encoding issue encountered attempting utf-8 decode.")
            refData = refFile.read()
            SaveReferences((ParseReference(refData, file)))




def QuickAdd(directory):
    """attempts to parse the newest file in the specified directory"""
    list_of_files = glob.glob('{dir}/*'.format(dir=directory)) # * means all if need specific format then *
    latest_file = max(list_of_files, key=os.path.getctime)
    OpenReference(latest_file)

def AddAll(directory):
    """attempts to parse every file in the specified directory"""
    list_of_files = glob.glob('{dir}/*'.format(dir=directory)) # * means all if need specific format then *
    for file in list_of_files:
        OpenReference(file)


LoadConfig()
if __name__ == "__main__":
    ref_db = LoadDatabase()
    command = sys.argv[1]

    ##write a command parser that can understand -- and - commands
    # add a head to the database that says which references has which tags 



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
    
    
    if command in ["set-db"]:
        try: 
            db = sys.argv[2]
            SaveConfig()
        except IndexError:
            print("Please specify a file path to the reference database")
    if command in ["set-tag"]:
        tags = sys.argv[2:]
        SaveConfig()
    if command in ["set-bib"]:
        try:
            bib_file = sys.argv[2]
            SaveConfig
        except IndexError:
            print("Please specify a file path to the working bibliography")
    
    
    if command in ["tag"]:
        tags = sys.argv[2:]
        SaveConfig()
    if command in ["export", "ex"]:
        bibliography = ''
        for key in ref_db.keys():
            if len(set(ref_db[key]["tags"]).union(tags)) != 0:
                bibliography += BibTexExport(ref_db[key])
        WriteBibliography(bibliography)


    if command in ["read"]:
        print("use the doi to get the pdf of the file")
    if command in ["search"]:
        print("specify tags/names ects to serach in the databse")
    
    WriteDatabase()