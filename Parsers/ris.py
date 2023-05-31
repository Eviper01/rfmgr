import rispy

def FormatInText(params):
    Authour = params[0][0]
    Authour = Authour.split(",")[1][1]+Authour.split(',')[0]
    date = params[1]
    date = date[2:4]
    return Authour+date

def FormatAuthours(params):
    authour_list = params[0] + params[1]
    return " and ".join(authour_list)

def FormatIdentity(params):
    return params[0]

def FormatPages(params):
    return params[0] + '-' + params[1]

def FormatYear(params):
    return params[0][2:4]


def parse(text, filename):
    try:
        with open(filename, "r") as file:
            data = rispy.load(file)
    except UnicodeDecodeError:
        print("ris.parse: Warning: UnicodeDecodeError, attempting utf-8 decode.")
        with open(filename, "r", encoding = "utf-8") as file:
            data = rispy.load(file)
    print(data[0])
    data = data[0]
    translations = [
                    ["InText",  ["first_authors", "year"],      FormatInText],
                    ["Authour", ["first_authors", "authors"],   FormatAuthours],
                    ["Title",   ["title"],                      FormatIdentity],
                    ["Journal", ["alternate_title3"],           FormatIdentity],
                    ["Volume",  ["volume"],                     FormatIdentity],
                    ["Number",  ["number"],                     FormatIdentity],
                    ["Pages",   ["start_page", "end_page"],     FormatPages],
                    ["Year",    ["year"],                       FormatYear],
                    ["DOI",     ["doi"],                        FormatIdentity]
                ]
    output = {}
    for translator in translations:
       key = translator[0]
       param_list = [data[fetch_key] for fetch_key in translator[1]]
       value = translator[2](param_list) 
       output[key] = value

    return output
