import os
import re
try:
    from parsemember import parseMember
except ImportError:
    from .parsemember import parseMember

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

class CppGetSetMaker:
    ClassNameRegExp = re.compile("^([@]+)([^<]*)(?:[<]([^>]+)[>])?$")
    def __init__(self, fileName):
        self.fileName = fileName
        self.className = self._classNameFromFileName() + "::"
        self.template = ""

    def _classNameFromFileName(self):
        return os.path.splitext(os.path.basename(self.fileName))[0]

    def _parseClassName(self, text):
        self.className = self.template = ""
        groups = CppGetSetMaker.ClassNameRegExp.match(text)
        if not groups:
            return
        if groups.group(2):
            self.className = groups.group(2) + "::"
        elif len(groups.group(1)) > 1:
            self.className = self._classNameFromFileName() + "::"
        if groups.group(3):
            params = []
            for param in (p.strip() for p in groups.group(3).split(",")):
                if len(param.split()) == 1:
                    params.append("typename " + param)
                else:
                    params.append(param)
            self.template = "template <%s>\n" % ", ".join(params)

    def parseLine(self, line):
        stripped = line.strip()
        if not stripped:
            return ""
        if stripped[0] == "@":
            self._parseClassName(stripped)
        else:
            props = parseMember(line, "lower-set")
            if props:
                props["class"] = self.className
                props["template"] = self.template
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
