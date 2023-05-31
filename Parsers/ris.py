def Identity(value):
    return value[0]

def Authours(authour_list):
    return " and ".join(authour_list)

def Dates(date):
    return date[0][0:4]

def InText(params):
    Authour = params[0]
    Authour = Authour.split(",")[1][1]+Authour.split(',')[0]
    date = params[1]
    date = date[2:4]
    return Authour+date

def parse(text):
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
        value = line[line.index("-")+1:].strip()
        data.append([key,value])
    #convert key values to others
    #translator is a list of output file key, data to get, data to pass.
    translations = [
                        ["InText",  ["A1", "PY"],   InText],
                        ["Authour", ["A1", "AU"],   Authours],
                        ["Title",   ["TI"],         Identity],
                        ["Journal", ["JF"],         Identity],
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
        value = key_set[2](param_list)
        parsed[key] = value
    return parsed
                