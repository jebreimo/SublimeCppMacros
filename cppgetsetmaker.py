import os
try:
    from parsemember import parseMember
except ImportError:
    from .parsemember import parseMember
try:
    from parseclassname import parseClassName
except ImportError:
    from .parseclassname import parseClassName

CppGetSetTemplate = """\
%(template)s%(type)s %(class)s%(get)s()%(get_suffix)s
{
%(indent)sreturn %(member)s;
}

%(template)svoid %(class)s%(set)s(%(type)s value)
{
%(indent)s%(member)s = value;
}
"""

def classNameFromFileName(fileName):
    if not fileName:
        return ""
    return os.path.splitext(os.path.basename(fileName))[0]

class CppGetSetMaker:
    def __init__(self, fileName):
        self.defaultClassName = classNameFromFileName(fileName)
        if not self.defaultClassName:
            self.defaultClassName = "CLASS"
        self.className = self.defaultClassName
        self.completeClassName = self.className + "::"
        self.templateSpec = ""

    def parseLine(self, line):
        stripped = line.strip()
        if not stripped:
            return ""
        if stripped[0] == "@":
            tempSpec, name, tempArgs = parseClassName(
                    stripped, self.className, self.defaultClassName)
            self.templateSpec = tempSpec and tempSpec + "\n"
            self.className = name
            self.completeClassName = name and name + tempArgs + "::"
        else:
            props = parseMember(line, "lower-get-set")
            if props:
                props["class"] = self.completeClassName
                props["template"] = self.templateSpec
                return CppGetSetTemplate % props
        return ""

if __name__ == "__main__":
    import sys

    def testCppGetSetMaker(args):
        if len(args) != 1:
            print("usage: %s <cpp file>" % os.path.basename(sys.argv[0]))
            return 1
        maker = CppGetSetMaker(args[0])
        for line in open(args[0]):
            result = maker.parseLine(line)
            if result:
                print(result)
        return 0

    sys.exit(testCppGetSetMaker(sys.argv[1:]))
