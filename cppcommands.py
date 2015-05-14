import sublime
import sublime_plugin
try:
    from parsemember import parseMember
except ImportError:
    from .parsemember import parseMember
try:
    from cppgetsetmaker import CppGetSetMaker
except ImportError:
    from .cppgetsetmaker import CppGetSetMaker
try:
    from cppimplmaker import CppImplMaker
except ImportError:
    from .cppimplmaker import CppImplMaker

HppGetSetTemplate = """\
%(indent)s%(static)s%(type)s %(get)s()%(get_suffix)s;
%(indent)s%(static)svoid %(set)s(%(type)s value);
"""

def selectFullLines(view, region):
    if region.a == region.b:
        return view.full_line(region)
    beg = region.begin()
    end = region.end()
    begClass = view.classify(beg)
    endClass = view.classify(end)
    if begClass & sublime.CLASS_LINE_END:
        beg += 1
    if endClass & sublime.CLASS_LINE_START:
        end -= 1
    if beg != region.begin() or end != region.end():
        region = sublime.Region(beg, end)
    return view.full_line(region)

class HppGetSetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        regions = []
        for reg in self.view.sel():
            reg = selectFullLines(self.view, reg)
            lines = []
            for rawLine in self.view.substr(reg).split("\n"):
                args = parseMember(rawLine, "lower-get-set")
                if args:
                    lines.append(HppGetSetTemplate % args)
            regions.append((reg, "\n".join(lines)))
        for reg, lin in reversed(regions):
            self.view.replace(edit, reg, lin)

class CppGetSetCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kw):
        sublime_plugin.TextCommand.__init__(self, *args, **kw)
        self.makers = {}

    def run(self, edit):
        bufferId = self.view.buffer_id()
        maker = self.makers.get(bufferId)
        if not maker:
            maker = CppGetSetMaker(self.view.file_name())
            self.makers[bufferId] = maker
        regions = []
        for reg in self.view.sel():
            reg = selectFullLines(self.view, reg)
            lines = []
            for rawLine in self.view.substr(reg).split("\n"):
                line = maker.parseLine(rawLine)
                if line:
                    lines.append(line)
            regions.append((reg, "\n".join(lines)))
        for reg, lin in reversed(regions):
            self.view.replace(edit, reg, lin)

class CppImplCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kw):
        sublime_plugin.TextCommand.__init__(self, *args, **kw)
        self.makers = {}

    def run(self, edit):
        bufferId = self.view.buffer_id()
        maker = self.makers.get(bufferId)
        if not maker:
            maker = CppImplMaker(self.view.file_name())
            self.makers[bufferId] = maker
        regions = []
        for reg in self.view.sel():
            reg = selectFullLines(self.view, reg)
            text = maker.parseText(self.view.substr(reg).split("\n"))
            if text:
                regions.append((reg, text))
        for reg, txt in reversed(regions):
            self.view.replace(edit, reg, txt)
