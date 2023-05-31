def Identity(value, refData, translator_info):
    try:
        return value[0]
    except IndexError:
        print("ris.parser: Error could not find necessary key")
        print(translator_info)
        return None

def Authours(authour_list, refData, translator_info):
    return " and ".join(authour_list)

def Dates(date, refData, translator_info ):
    try:
        return date[0][0:4]
    except IndexError:
        print("ris.parse: Warning no date information found")
        print(refData)
        return None  

def InText(params, refData, translator_info):
    try:
        Authour = params[0]
        Authour = Authour.split(",")[1][1]+Authour.split(',')[0]
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
    return Authour+date

def parse(text, filename):
    """Parses .ris files native to endnote"""
    refs = text.split("\n\n")
    output = []
    for ref in refs:
        output.append(refParse(ref))
    return output 

def refParse(text):
    lines = text.split("\n")
    data = []
    #get key values
    for line in lines:
        key = line.split("-")[0].strip()
        try:
            value = line[line.index("-")+1:].strip()
        except ValueError:
            print("ris.parse: Warning: substring issue")
            print(line)
            value = ""
        data.append([key,value])
    #convert key values to others
    #translator is a list of output file key, data to get, data to pass.
    translations = [
                        ["InText",  ["A1", "PY"],   InText],
                        ["Authour", ["A1", "AU"],   Authours],
                        ["Title",   ["TI"],         Identity],
                        ["Journal", ["JF", "T2"],   Identity],
                        ["Volume",  ["VL"],         Identity],
                        ["Number",  ["IS"],         Identity],
                        ["Pages",   ["SP"],         Identity],
                        ["Year",    ["PY"],         Dates],
                        ["DOI",     ["DO"],         Identity]
                    ]

    #run through each of the refernces in this file
    parsed = {}
    for key_set in translations:
        key = key_set[0]
        param_list = []
        for id in key_set[1]:
            param_list += [dataline[1] for dataline in data if dataline[0] == id]
        value = key_set[2](param_list, data, key_set)
        if value != None:
            parsed[key] = value
    return parsed
                