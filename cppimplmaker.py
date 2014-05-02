import os
import re
try:
    from parseclassname import parseClassName
except ImportError:
    from .parseclassname import parseClassName

DefaultIndentation = "    "

def classNameFromFileName(fileName):
    if not fileName:
        return ""
    return os.path.splitext(os.path.basename(fileName))[0]

def removeComments(line, multilineActive):
    if multilineActive:
        pos = line.find("*/")
        if pos == -1:
            return "", True
        else:
            line = line[pos + 2:]
    while True:
        slPos = line.find("//")
        mlPos = line.find("/*")
        if slPos != -1 and (mlPos == -1 or slPos < mlPos):
            return line[:slPos], False
        elif mlPos != -1:
            pos = line.find("*/", mlPos + 2)
            if pos == -1:
                return line[:mlPos], True
            else:
                line = line[:mlPos] + line[pos + 2:]
        else:
            return line, False

def extractCode(lines):
    code = []
    codeLines = None
    mlComment = False
    for line in lines:
        line, mlComment = removeComments(line, mlComment)
        line = line.rstrip()
        stripped = line.lstrip()
        if not stripped:
            pass
        elif line[-1] == ":" and line[-2:] != "::":
            codeLines = None
        elif stripped[0] == "@":
            code.append([stripped])
            codeLines = None
        else:
            if not codeLines:
                codeLines = []
                code.append(codeLines)
            codeLines.append(line)
            if line.endswith(";"):
                codeLines = None
    return code

def findStartOfArgs(line):
    pos = line.find("(")
    if pos == -1:
        return -1
    if line[:pos].rstrip().endswith("operator"):
        pos = line.find("(", pos + 1)
        if pos == -1:
            return -1
    return pos

def findEndOfArgs(line, openParens):
    prevPos = 0
    while True:
        pos = line.find(")", prevPos)
        if pos == -1:
            return -1, openParens + line[prevPos:].count("(")
        openParens += line[prevPos:pos].count("(") - 1
        if openParens == 0:
            return pos, 0
        prevPos = pos + 1

def appendIfNonEmpty(l, s):
    if s:
        l.append(s)

def splitFunction(lines):
    prefix = []
    args = []
    suffix = []
    remainder = []
    for i, line in enumerate(lines):
        pos = findStartOfArgs(line)
        if pos != -1:
            appendIfNonEmpty(prefix, line[:pos].strip())
            appendIfNonEmpty(remainder, line[pos + 1:].strip())
            remainder.extend(l.strip() for l in lines[i + 1:])
            break
        else:
            prefix.append(line.strip())
    if not prefix or not remainder:
        raise Exception("Doesn't look like a function.")
    openParens = 1
    for i, line in enumerate(remainder):
        pos, openParens = findEndOfArgs(line, openParens)
        if pos != -1:
            appendIfNonEmpty(args, line[:pos].rstrip())
            appendIfNonEmpty(suffix, line[pos + 1:].strip())
            suffix.extend(remainder[i + 1:])
            break
        else:
            args.append(line)
    return prefix, args, suffix

ArgRE = re.compile(r" *\=[^,]+")

def cleanArguments(lines):
    result = []
    for line in lines:
        arg = ArgRE.sub("", line.strip())
        if arg:
            result.append(arg)
    return result

def isIdentifier(c):
    return c.isalnum() or c == "_"

def findWord(s, w):
    start = s.find(w)
    while start != -1:
        end = start + len(w)
        front = "" if start == 0 else s[start - 1]
        back = "" if end == len(s) else s[end]
        if not isIdentifier(front) and not isIdentifier(back):
            return start
        start = s.find(w, end)
    return -1

def findEndOfTemplate(line, openParens=0):
    prevPos = 0
    while True:
        pos = line.find(">", prevPos)
        if pos == -1:
            return -1, openParens + line[prevPos:].count("<")
        openParens += line[prevPos:pos].count("<") - 1
        if openParens == 0:
            return pos + 1, 0
        prevPos = pos + 1

def extractTemplateSpec(lines):
    if not lines or not findWord(lines[0], "template") == 0:
        return [], lines
    tpl = []
    prefix = []
    openParens = 0
    for i, line in enumerate(lines):
        pos, openParens = findEndOfTemplate(line, openParens)
        if pos != -1:
            tpl.extend(lines[:i])
            appendIfNonEmpty(tpl, line[:pos])
            appendIfNonEmpty(prefix, line[pos:])
            prefix.extend(lines[i + 1:])
            break
    return tpl, prefix

NameRE = re.compile(r"[0-9A-Za-z_~]\w*$")

def splitFunctionPrefix(lines):
    prefix = lines[:-1]
    pos = findWord(lines[-1], "operator")
    if pos == -1:
        match = NameRE.search(lines[-1])
        if not match:
            raise Exception("Can't find name of function")
        pos = match.start(0)
    appendIfNonEmpty(prefix, lines[-1][:pos].strip())
    name = lines[-1][pos:].lstrip()
    tpl, prefix = extractTemplateSpec(prefix)
    return tpl, prefix, name

def removeWord(s, w):
    start = s.find(w)
    while start != -1:
        end = start + len(w)
        front = "" if start == 0 else s[start - 1]
        back = "" if end == len(s) else s[end]
        if not isIdentifier(front) and not isIdentifier(back):
            # Not part of a longer word
            if front.isspace():
                start -= 1
            elif back.isspace():
                end += 1
            s = s[:start] + s[end:]
        else:
            start = end
        start = s.find(w, start)
    return s

def cleanPrefix(lines, isMember):
    result = []
    for line in lines:
        line = removeWord(line, "virtual")
        line = removeWord(line, "explicit")
        if isMember:
            line = removeWord(line, "static")
        line = line.strip()
        appendIfNonEmpty(result, line)
    return result

def getIndentation(s):
    i = 0
    while i < len(s) and s[i].isspace():
        i += 1
    if i != 0:
        return s[:i]
    else:
        return "    "

def getReturnValue(lines):
    line = removeWord(" ".join(lines), "const").strip()
    if not line or line == "void" or line[-1] == "&":
        return ""
    elif line[-1] == "*":
        return "nullptr"
    else:
        return line + "()"

def parseFunction(lines, className):
    d = {"class": className}
    d["indentation"] = getIndentation(lines[0])
    pre, args, suf = splitFunction(lines)
    tpl, pre, name = splitFunctionPrefix(pre)
    d["template"] = tpl
    d["name"] = name
    pre = cleanPrefix(pre, className)
    d["return"] = pre
    d["value"] = getReturnValue(pre)
    args = cleanArguments(args)
    d["arguments"] = args
    if suf:
        suf[-1] = suf[-1][:-1]
    d["suffix"] = [s for s in suf if s]
    return d

def getImplementation(func):
    lines = []
    if func["template"]:
        lines.extend(func["template"]) # TODO: fix indentation
    if not func["return"]:
        line = []
    elif len(func["return"][-1]) < 60:
        lines.extend(func["return"][:-1])
        line = [func["return"][-1], " "]
    else:
        lines.extend(func["return"])
        line = []

    if func.get("class"):
        line.append(func["class"])
        line.append("::")
    line.append(func["name"])
    line.append("(")
    if func["arguments"]:
        argIndent = " " * sum(len(s) for s in line)
        line.append(func["arguments"][0])
        lines.append("".join(line))
        for line in func["arguments"][1:]:
            lines.append(argIndent + line)
        lines[-1] += ")"
    else:
        lines.append("".join(line) + ")")
    if func["suffix"]:
        lines[-1] += " " + func["suffix"][0]
        lines.extend((func["indentation"] + s) for s in func["suffix"][1:])
    lines.append("{")
    if func["value"]:
        lines.append(func["indentation"] + "return " + func["value"] + ";")
    lines.append("}\n")
    return "\n".join(lines)

class CppImplMaker:
    def __init__(self, fileName):
        self.defaultClassName = classNameFromFileName(fileName)
        if not self.defaultClassName:
            self.defaultClassName = "CLASS"
        self.className = self.defaultClassName
        self.completeClassName = self.className
        self.templateSpec = ""

    def parseText(self, lines):
        decls = extractCode(lines)
        code = []
        for lines in decls:
            if len(lines) == 1 and lines[0][0] == "@":
                tempSpec, name, tempArgs = parseClassName(
                        lines[0], self.className, self.defaultClassName)
                self.templateSpec = tempSpec and tempSpec
                self.className = name
                self.completeClassName = name and name + tempArgs
            else:
                try:
                    d = parseFunction(lines, self.completeClassName)
                    if not d.get("template") and self.templateSpec:
                        d["template"] = [self.templateSpec]
                    code.append(getImplementation(d))
                except Exception as ex:
                    code.append("// " + str(ex) + "\n" + "\n".join(lines))
        return "\n".join(code)

if __name__ == "__main__":
    import sys

    def testCppImplMaker(args):
        if len(args) != 1:
            print("usage: %s <cpp file>" % os.path.basename(sys.argv[0]))
            return 1
        maker = CppImplMaker(args[0])
        print(maker.parseText(open(args[0])))
        return 0

    sys.exit(testCppImplMaker(sys.argv[1:]))
