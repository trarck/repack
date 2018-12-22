import sys
import os
from infos import *
from clang import cindex


class ObjcParser(object):
    def __init__(self, opts):
        self.index = cindex.Index.create()
        self.clang_args = opts['clang_args']
        self.skip_classes = {}
        self.parsed_classes = {}
        self.win32_clang_flags = opts['win32_clang_flags']
        self.methods = []
        self.namespaces = []

        self.current_namespace = None
        self._parsing_file = None

        extend_clang_args = []

        for clang_arg in self.clang_args:
            if not os.path.exists(clang_arg.replace("-I", "")):
                pos = clang_arg.find("lib/clang/3.3/include")
                if -1 != pos:
                    extend_clang_arg = clang_arg.replace("3.3", "3.4")
                    if os.path.exists(extend_clang_arg.replace("-I", "")):
                        extend_clang_args.append(extend_clang_arg)

        if len(extend_clang_args) > 0:
            self.clang_args.extend(extend_clang_args)

        if sys.platform == 'win32' and self.win32_clang_flags != None:
            self.clang_args.extend(self.win32_clang_flags)

        # if opts['skip']:
        #     list_of_skips = re.split(",\n?", opts['skip'])
        #     for skip in list_of_skips:
        #         class_name, methods = skip.split("::")
        #         self.skip_classes[class_name] = []
        #         match = re.match("\[([^]]+)\]", methods)
        #         if match:
        #             self.skip_classes[class_name] = match.group(1).split(" ")
        #         else:
        #             raise Exception("invalid list of skip methods")

    @staticmethod
    def in_parse_file(cursor, parsing_file):
        if cursor.location and cursor.location.file:
            source_file = cursor.location.file.name
        elif cursor.extent and cursor.extent.start:
            source_file = cursor.extent.start.file.name

        source_file = source_file.replace("\\", "/")
        # print("%s=%s" % (source_file, parsing_file))
        return source_file == parsing_file

    def _check_diagnostics(self, diagnostics):
        errors = []
        for idx, d in enumerate(diagnostics):
            if d.severity > 2:
                errors.append(d)
        if len(errors) == 0:
            return
        print("====\nErrors in parsing headers:")
        severities = ['Ignored', 'Note', 'Warning', 'Error', 'Fatal']
        for idx, d in enumerate(errors):
            print "%s. <severity = %s,\n    location = %r,\n    details = %r>" % (
                idx + 1, severities[d.severity], d.location, d.spelling)
        print("====\n")

    # must read the yaml file first
    def parse_file(self, file_path):
        tu = self.index.parse(file_path, self.clang_args)
        if len(tu.diagnostics) > 0:
            self._check_diagnostics(tu.diagnostics)
            is_fatal = False
            for d in tu.diagnostics:
                if d.severity >= cindex.Diagnostic.Error:
                    is_fatal = True
            if is_fatal:
                print("*** Found errors - can not continue")
                raise Exception("Fatal error in parsing headers")
        self._parsing_file = file_path.replace("\\", "/")

        # the root cursor is TRANSLATION_UNIT,visitor children
        if tu.cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            cd = Parser._get_children_array_from_iter(tu.cursor.get_children())
            for cursor in tu.cursor.get_children():
                self._traverse(cursor)

    @staticmethod
    def _get_children_array_from_iter(cursor_iter):
        children = []
        for child in cursor_iter:
            children.append(child)
        return children

    def _traverse(self, cursor):
        if not Parser.in_parse_file(cursor, self._parsing_file):
            return None

        if cursor.kind == cindex.CursorKind.CLASS_DECL:
            # print("find class")
            if cursor == cursor.type.get_declaration() and len(
                    Parser._get_children_array_from_iter(cursor.get_children())) > 0:

                if not self.parsed_classes.has_key(cursor.displayname):
                    nclass = ClassInfo(cursor)
                    self.parsed_classes[cursor.displayname] = nclass
                return
        elif cursor.kind == cindex.CursorKind.FUNCTION_DECL:
            # print("find function")
            fun = FunctionInfo(cursor)
            self.methods.append(fun)
        elif cursor.kind == cindex.CursorKind.CXX_METHOD:
            # print("find method")
            method = FunctionInfo(cursor)
            self.methods.append(method)
        elif cursor.kind == cindex.CursorKind.NAMESPACE:
            # print("find namespace")
            self.current_namespace = cursor.spelling
            for sub_cursor in cursor.get_children():
                self._traverse(sub_cursor)
            self.current_namespace = None
        elif cursor.kind == cindex.CursorKind.CONSTRUCTOR:
            # print("find CONSTRUCTOR")
            method = FunctionInfo(cursor)
            self.methods.append(method)
        elif cursor.kind == cindex.CursorKind.DESTRUCTOR:
            # print("find DESTRUCTOR")
            method = FunctionInfo(cursor)
            self.methods.append(method)
        elif cursor.kind == cindex.CursorKind.OBJC_INTERFACE_DECL:
            print("find objc define")

    def sorted_classes(self):
        """
        sorted classes in order of inheritance
        """
        sorted_list = []
        for class_name in self.parsed_classes.iterkeys():
            nclass = self.parsed_classes[class_name]
            sorted_list += self._sorted_parents(nclass)
        # remove dupes from the list
        no_dupes = []
        [no_dupes.append(i) for i in sorted_list if not no_dupes.count(i)]
        return no_dupes

    def _sorted_parents(self, nclass):
        """
        returns the sorted list of parents for a native class
        """
        sorted_parents = []
        for p in nclass.parents:
            if p.class_name in self.parsed_classes.keys():
                sorted_parents += self._sorted_parents(p)
        if nclass.class_name in self.parsed_classes.keys():
            sorted_parents.append(nclass.class_name)
        return sorted_parents
