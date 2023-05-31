def parse(text):
    references = text.split("\n\n")
    outputs = []
    for ref in references:
        outputs.append(refParse(ref))
    return outputs

def refParse(text):
    lines = text.split(",")
    data = []
    for line in lines:
        print("line:")
        print(line)
    exit()
    #get key values
    for line in lines:
        key = line.split("=")[0].strip()
        try:
            value = line[line.index("=")+1:].strip()
            data.append([key,value])
        except:
            print(line)
    print(data)
    exit()