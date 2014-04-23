import re

DataMemberRE = re.compile(r"(?P<indent>[ \t]*)(?P<type>.+?)[ ]+(?P<prefix>[ms]_)(?P<name>[^ /\t;]+?);")

def _parseMember(line):
    if not line:
        return None
    m = DataMemberRE.match(line)
    if not m:
        return None
    else:
        d = {"indent": m.group("indent") or "    ",
             "static": "",
             "type": m.group("type"),
             "mutable": False,
             "name": m.group("name"),
             "member": m.group("prefix") + m.group("name"),
             "get_suffix": " const"}
        if m.group("type").startswith("static "):
            d["type"] = m.group("type")[7:]
            d["static"] = "static "
            d["get_suffix"] = ""
        elif m.group("type").startswith("mutable "):
            d["type"] = m.group("type")[8:]
            d["mutable"] = True
        return d

def isClassType(s):
    return (s[-1] not in "&*" and
            not (s.islower() and s.isalpha()) and
            not s.endswith("_t") or
            s.endswith("string"))

def lowerNoGet(args):
    return args["lowerName"], "set" + args["upperName"]

def lowerNoGetNoSet(args):
    return args["lowerName"], args["lowerName"]

def upperNoGet(args):
    return args["upperName"], "Set" + args["upperName"]

def upperNoGetNoSet(args):
    return args["upperName"], args["upperName"]

def lowerGet(args):
    return "get" + args["upperName"], "set" + args["upperName"]

def upperGet(args):
    return "Get" + args["upperName"], "Set" + args["upperName"]

def getNameFunction(key):
    if key == "lower-get-set":
        return lowerGet
    if key == "upper-get-set":
        return upperGet
    if key == "upper-set":
        return upperNoGet
    if key == "lower":
        return lowerNoGetNoSet
    if key == "upper":
        return upperNoGetNoSet
    return lowerNoGet

def parseMember(line, nameStyle):
    args = _parseMember(line)
    if not args:
        return None
    name = args["name"]
    t = args["type"]
    if t.startswith("std::auto_ptr"):
        m, n = t.find("<"), t.rfind(">")
        if m != -1 and n != -1:
            args["type"] = t[m + 1:n] + "*"
    elif isClassType(t):
        args["type"] = "const %s&" % args["type"]
    args["lowerName"] = name[0].lower() + name[1:]
    args["upperName"] = name[0].upper() + name[1:]
    nameFunc = getNameFunction(nameStyle)
    args["get"], args["set"] = nameFunc(args)
    return args
