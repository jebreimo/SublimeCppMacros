def findEndOfTepmplateSpec(line, startPos):
    i = startPos + 1
    n = len(line)
    count = 1
    while i < n:
        if line[i] == "<":
            count += 1
        elif line[i] == ">":
            count -= 1
            if count == 0:
                return i + 1
        i += 1
    return -1

def splitNameString(line):
    parts = []
    count = 0
    n = len(line)
    i = start = 1
    while i < n:
        if line[i] == "<":
            if start != i:
                parts.append(line[start:i])
            inext = findEndOfTepmplateSpec(line, i)
            if inext == -1:
                return parts
            parts.append(line[i:inext])
            i = start = inext
        else:
            i += 1
    if start != n:
        parts.append(line[start:])
    return parts


def parseTemplateSpec(line):
    spec = []
    args = []
    for param in (s.strip() for s in line[1:-1].split(",")):
        parts = param.split()
        if not parts[0]:
            pass
        elif len(parts) == 1:
            spec.append("typename " + parts[0])
            args.append(param)
        elif parts[0] == "typename":
            spec.append(param)
            args.append(parts[-1])
        else:
            spec.append(param)
            args.append(parts[-1])
    return ("template <%s>" % ", ".join(spec),
            "<%s>" % ", ".join(args))

def parseClassName(line, currentName, defaultName):
    parts = splitNameString(line)
    if not parts or len(parts) > 3:
        return "", "", ""
    tempSpec, name, tempArgs = "", "", ""
    if parts[0][0] == "<":
        tempSpec, tempArgs = parseTemplateSpec(parts[0])
        if len(parts) == 1:
            tempArgs = ""
        elif len(parts) == 3:
            name, tempArgs = parts[1], parts[2]
        elif parts[1][0] == "<":
            tempArgs = parts[1]
        else:
            name = parts[1]
    else:
        name = parts[0]
        if len(parts) == 2:
            tempSpec = "<>"
            tempArgs = parts[1]
    if name == "@":
        name = defaultName
    elif name == "@@":
        name = currentName
    if name:
        name = name
    return tempSpec, name, tempArgs
