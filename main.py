import sys
import os
import glob
import pprint
import json
import importlib
import sys
import webbrowser
sys.path.append(__file__+'/../Parsers/')
configPath =  os.getenv('APPDATA') + '/rfmgr/config.json'
print(configPath)
db = None
tags = []
bib_file = None
ref_db = None



class RISParser:
    def Identity(self, value, refData, translator_info):
        try:
            return value[0]
        except IndexError:
            print("ris.parser: Error could not find necessary key")
            print(translator_info)
            return None

    def Authours(self, authour_list, refData, translator_info):
        return " and ".join(authour_list)

    def Dates(self, date, refData, translator_info):
        try:
            return date[0][0:4]
        except IndexError:
            print("ris.parse: Warning no date information found")
            print(refData)
            return None

    def InText(self, params, refData, translator_info):
        try:
            Authour = params[0]
            Authour = Authour.split(",")[1][1] + Authour.split(',')[0]
        except IndexError:
            print(params)
            print("ris.parser: Warning failed to generate InText Reference")
            try:
                cite_key = [pairs[1] for pairs in refData if pairs[0] == "C1"][0]
                print("Found cite_key at 'C1'", cite_key)
            except IndexError:
                print("Could not find alternative citekeys")
                print(refData)
                cite_key = input("Please manually specify cite_key >")
            return cite_key
        date = params[1]
        date = date[2:4]
        return Authour + date

    def parse(self, text, filename):
        """Parses .ris files native to endnote"""
        refs = text.split("\n\n")
        output = []
        for ref in refs:
            output.append(self.refParse(ref))
        return output

    def refParse(self, text):
        lines = text.split("\n")
        data = []
        # get key values
        for line in lines:
            key = line.split("-")[0].strip()
            try:
                value = line[line.index("-") + 1:].strip()
            except ValueError:
                print("ris.parse: Warning: substring issue")
                print(line)
                value = ""
            data.append([key, value])
        # convert key values to others
        # translator is a list of output file key, data to get, data to pass.
        translations = [
            ["InText", ["A1", "PY"], self.InText],
            ["Authour", ["A1", "AU"], self.Authours],
            ["Title", ["TI"], self.Identity],
            ["Journal", ["JF", "T2"], self.Identity],
            ["Volume", ["VL"], self.Identity],
            ["Number", ["IS"], self.Identity],
            ["Pages", ["SP"], self.Identity],
            ["Year", ["PY"], self.Dates],
            ["DOI", ["DO"], self.Identity]
        ]

        # run through each of the references in this file
        parsed = {}
        for key_set in translations:
            key = key_set[0]
            param_list = []
            for id in key_set[1]:
                param_list += [dataline[1] for dataline in data if dataline[0] == id]
            value = key_set[2](param_list, data, key_set)
            if value is not None:
                parsed[key] = value
        return parsed






parsers = {"ris":RISParser}

def ParseReference(text, filename):
    """Passes the text in the ref file to the relvant parser returns in dictionary of key value pairs that have the same names and formatting as bibtex however 'ref' is used to denote the refernce identifier """
    extension = filename.split(".")[-1]
    if extension in parsers.keys():
        parser = parsers[extension]()
        return parser.parse(text=text, filename=filename)
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
        with open(configPath,"r") as file:
            config = json.load(file)
            print(config)
    except FileNotFoundError:
        print("config.json file not found, will create one instead")
        MissingConfig = True
    try:
        db = config['db']
    except KeyError:
        db = os.getenv('APPDATA') + '/rfmgr/db.json'
        print('database pointer missing defaulting to', db)
    except UnboundLocalError:
        db = os.getenv('APPDATA') + '/rfmgr/db.json'
        print('database pointer missing defaulting to', db)
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
        bib_file = os.getenv('APPDATA') + '/rfmgr/bibfile.bib'
        print("defaulting to", bib_file)
    except UnboundLocalError:
        bib_file = os.getenv('APPDATA') + '/rfmgr/bibfile.bib' 
        print("bib file defaulting to", bib_file) 
    if MissingConfig:
        os.makedirs(os.getenv('APPDATA') + '/rfmgr/')
        with open(configPath,"x") as file:
            config = {
                        'db': db,
                        'tags': tags,
                        'bib_file': bib_file 
                    }
            file.write(json.dumps(config, indent = 4))

def SaveConfig():
    with open(configPath,"w") as file:
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
    try:
        command = sys.argv[1]
    except IndexError:
        print("Usage: rfmgr [command] [paramters]")
        command = None
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


    if command in ["open", "read"]:
        for cite_key in sys.argv[2:]:
            try:
                webbrowser.open('https://doi.org/'+ ref_db[cite_key]["DOI"])
            except KeyError:
                print("Invalid refernce key")
    if command in ["search"]:
        print("specify tags/names ects to serach in the databse")
    
    WriteDatabase()