import re


class NamespaceInfo:
    def __init__(self, name, start_line, parent_name=None):
        self.name = name
        self.start_line = start_line
        self.end_line = -1
        self.bracket_start = None
        self.parent_name = parent_name


class BracketInfo:
    Bracket_Namespace = 1
    Bracket_Class = 2
    Bracket_Method = 3
    Bracket_Other = 10

    def __init__(self, start_line, start_col, bracket_type):
        self.start_line = start_line
        self.start_col = start_col
        self.bracket_type = bracket_type


class ClassInfo:
    def __init__(self, class_name, namespace, start_line):
        self.name = class_name
        self.namespace = namespace
        self.start_line = start_line
        self.end_line = -1
        # self.fields = []
        # self.methods = []
        self.bracket_start = None


class MethodInfo:
    def __init__(self, name, class_name, start_line):
        self.name = name
        self.class_name = class_name
        self.start_line = start_line
        self.end_line = -1
        self.bracket_start = None


class CppFileParser:
    def __init__(self, macros=None):
        self.namespace_stack = []
        self.namespaces = []
        self.current_namespace = None
        self.bracket_stack = []
        self.macros = macros

    def _parse_namespace(self, line, line_index, lines, pos=0):

        # check have namespace
        if not re.search(r'\s*namespace\s+', line):
            return line_index, pos

        namespace_pos = line.find("namespace", pos)
        if namespace_pos > -1:
            # check is using namespace
            if line.find("using") > -1:
                return line_index + 1, 0

            namespace_pos += len("namespace")
            bracket_pos = line.find("{", namespace_pos)
            if bracket_pos > -1:

                # create namespace
                namespace_name = line[namespace_pos:bracket_pos].strip()
                print("find namespace name:%s" % namespace_name)

                if bracket_pos + 1 < len(line) - 1:
                    is_end_line = False
                else:
                    is_end_line = True
            else:
                namespace_name = line[namespace_pos:].strip()
                is_end_line = True

            if self.current_namespace:
                self.namespace_stack.append(self.current_namespace)

            self.current_namespace = NamespaceInfo(namespace_name, line_index)
            self.namespaces.append(self.current_namespace)

            if bracket_pos > -1:
                # create namespace bracket
                bracket_info = BracketInfo(line_index, bracket_pos + 1, BracketInfo.Bracket_Namespace)
                self.bracket_stack.append(bracket_info)
                self.current_namespace.bracket_start = bracket_info

            # maybe have sub namespace
            if is_end_line:
                return line_index + 1, 0
            else:
                return line_index, bracket_pos + 1

    def _parse_comment(self, line, line_index, lines):
        if line.startswith("//"):
            return line_index, None

        pos = line.find("//")
        if pos > 0:
            return line_index, line[:pos]

        pos = line.find("/*")
        if pos > -1:
            # print("find comment %d" % line_index)
            if pos > 0:
                new_line = line[:pos]
            else:
                new_line = None

            lines_count = len(lines)
            while line_index < lines_count:

                pos = line.find("*/")

                # print("%s,%d:%d" % (line, line_index, pos))
                if pos > -1:
                    # print("find comment end %d" % line_index)
                    # print("%d:%d" % (pos + 2, len(line) - 1))
                    if pos + 2 < len(line) - 1:
                        if new_line:
                            new_line += line[pos:]
                        else:
                            new_line = line[pos:]
                    break
                line_index += 1
                line = lines[line_index].strip()

            return line_index, new_line

        return line_index, line

    def _parse_macro(self, line):
        if self.macros:
            for k, v in self.macros.items():
                line = line.replace(k, v)
        return line


class CppHeadFileParser(CppFileParser):
    def __init__(self, macros=None):
        CppFileParser.__init__(self, macros)
        self.classes = []
        self.current_class = None

    def _check_is_class_pre_declare(self, line, line_index, lines, pos):
        pos = line.find(";", pos)
        if pos > -1:
            return True
        pos = line.find("{")
        if pos > -1:
            return False

        # check next line
        lines_count = len(lines)
        line_index += 1
        while line_index < lines_count:
            line = lines[line_index].strip()
            if line:
                if line.startswith(";"):
                    return True
                elif line.startswith("{"):
                    return False
                else:
                    raise "get class error"
        raise "get class error"

    def _parse_class(self, line, line_index, lines, pos=0):
        # check have class
        if not re.search(r'\s*class\s+', line):
            return line_index, pos

        class_pos = line.find("class", pos)
        class_pos += len("class")
        if self._check_is_class_pre_declare(line, line_index, lines, class_pos):
            # print("find class pre declare %d" % line_index)
            return line_index + 1, 0

        # get class name
        class_define = None
        parent_position = line.find(":", class_pos)
        if parent_position > -1:
            class_define = line[class_pos:parent_position].strip()

        bracket_pos = line.find("{", class_pos)

        if class_define is None:
            if bracket_pos > -1:
                class_define = line[class_pos:bracket_pos].strip()
            else:
                class_define = line[class_pos:].strip()

        segs = class_define.split(" ")
        class_name = segs[-1]
        print("find class name:%s" % class_name)

        if self.current_class:
            print "===>inner class find .name %s" % class_name
        else:
            namespace_name = None
            if self.current_namespace:
                namespace_name = self.current_namespace.name
            self.current_class = ClassInfo(class_name, namespace_name, line_index)
            self.classes.append(self.current_class)

        if bracket_pos > -1:
            # create class bracket
            bracket_info = BracketInfo(line_index, bracket_pos + 1, BracketInfo.Bracket_Class)
            self.bracket_stack.append(bracket_info)
            self.current_class.bracket_start = bracket_info

            if bracket_pos == len(line) - 1:
                is_end_line = False
            else:
                is_end_line = True
        else:
            is_end_line = True

        if is_end_line:
            return line_index + 1, 0
        else:
            return line_index, bracket_pos + 1

    def _parse_bracket(self, line, line_index, lines, pos=0):

        bracket_begin_pos = line.find("{", pos)
        if bracket_begin_pos > -1:
            if self.current_namespace and self.current_namespace.bracket_start is None:
                bracket_info = BracketInfo(line_index, bracket_begin_pos + 1, BracketInfo.Bracket_Namespace)
                self.current_namespace.bracket_start = bracket_info
            elif self.current_class and self.current_class.bracket_start is None:
                bracket_info = BracketInfo(line_index, bracket_begin_pos + 1, BracketInfo.Bracket_Class)
                self.current_class.bracket_start = bracket_info
            else:
                bracket_info = BracketInfo(line_index, bracket_begin_pos + 1, BracketInfo.Bracket_Other)

            self.bracket_stack.append(bracket_info)

            # print("bracket start %d,%d:%d" % (line_index, bracket_begin_pos, bracket_info.bracket_type))

            if bracket_begin_pos == len(line) - 1:
                return line_index + 1, 0
            else:
                return line_index, bracket_begin_pos + 1

        bracket_end_pos = line.find("}", pos)
        if bracket_end_pos > -1:
            # print("bracket end %d,%d:%d" % (line_index, bracket_begin_pos, len(self.bracket_stack)))

            bracket_info = self.bracket_stack.pop()
            if bracket_info.bracket_type == BracketInfo.Bracket_Namespace:
                if self.current_namespace:
                    self.current_namespace.end_line = line_index
                    if len(self.namespace_stack) > 0:
                        self.current_namespace = self.namespace_stack.pop()
                    else:
                        self.current_namespace = None
                else:
                    print("===>err! namespace is close before. current line %d" % line_index)

            elif bracket_info.bracket_type == BracketInfo.Bracket_Class:
                if self.current_class:
                    self.current_class.end_line = line_index
                    self.current_class = None
                else:
                    print("===>err! class is close before. current line %d" % line_index)

            if bracket_end_pos == len(line) - 1:
                return line_index + 1, 0
            else:
                return line_index, bracket_end_pos + 1

        return line_index + 1, 0

    def parse(self, lines):

        line_index = 0
        col = 0
        line_length = len(lines)
        while line_index < line_length:
            # print("parse line:%d" % line_index)
            line = lines[line_index].strip()

            if line:
                line_index, line = self._parse_comment(line, line_index, lines)

                if line:
                    line = self._parse_macro(line)
                    next_line_index, col = self._parse_namespace(line, line_index, lines, col)
                    if next_line_index == line_index:
                        next_line_index, col = self._parse_class(line, line_index, lines, col)

                        if next_line_index == line_index:
                            next_line_index, col = self._parse_bracket(line, line_index, lines, col)

                    line_index = next_line_index
                else:
                    line_index += 1
            else:
                line_index += 1


class CppSourceFileParser(CppFileParser):
    def __init__(self, macros=None):
        CppFileParser.__init__(self, macros)
        self.namespaces = []
        self.methods = []
        self.current_method = None

    def _check_is_function_define(self, line, line_index, lines, pos):
        pos = line.find("{")
        if pos > -1:
            return True

        pos = line.find(";")
        if pos > -1:
            return False

        lines_count = len(lines)
        line_index += 1
        while line_index < lines_count:
            line = lines[line_index].strip()

            if line:
                line_index, line = self._parse_comment(line, line_index, lines)

                if line:
                    line = self._parse_macro(line)

                    pos = line.find("{")
                    if pos > -1:
                        return True

                    pos = line.find(";")
                    if pos > -1:
                        return False

            line_index += 1

    def _parse_method(self, line, line_index, lines, pos=0):
        # check have class
        m = re.search(r'\s*(.*)::(.*)\s*\(', line)
        if not m:
            return line_index, pos

        class_pos = line.find("class", pos)
        class_pos += len("class")
        if not self._check_is_function_define(line, line_index, lines, class_pos):
            # print("find function call %d" % line_index)
            return line_index + 1, 0

        # get class name
        class_name = m.group(1)
        method_name = m.group(2)
        # print("find method name:%s::%s" % (class_name, method_name))

        if self.current_method:
            print "===>err method define not close %s::%s" % (self.current_method.class_name, self.current_method.name)
        else:
            self.current_method = MethodInfo(method_name, class_name, line_index)
            self.methods.append(self.current_method)

        bracket_pos = line.find("{", class_pos)
        if bracket_pos > -1:
            # create class bracket
            bracket_info = BracketInfo(line_index, bracket_pos + 1, BracketInfo.Bracket_Class)
            self.bracket_stack.append(bracket_info)
            self.current_method.bracket_start = bracket_info

            if bracket_pos == len(line) - 1:
                is_end_line = False
            else:
                is_end_line = True
        else:
            is_end_line = True

        if is_end_line:
            return line_index + 1, 0
        else:
            return line_index, bracket_pos + 1

    def _parse_bracket(self, line, line_index, lines, pos=0):

        bracket_begin_pos = line.find("{", pos)
        if bracket_begin_pos > -1:
            if self.current_namespace and self.current_namespace.bracket_start is None:
                bracket_info = BracketInfo(line_index, bracket_begin_pos + 1, BracketInfo.Bracket_Namespace)
                self.current_namespace.bracket_start = bracket_info
            elif self.current_method and self.current_method.bracket_start is None:
                bracket_info = BracketInfo(line_index, bracket_begin_pos + 1, BracketInfo.Bracket_Method)
                self.current_method.bracket_start = bracket_info
            else:
                bracket_info = BracketInfo(line_index, bracket_begin_pos + 1, BracketInfo.Bracket_Other)

            self.bracket_stack.append(bracket_info)

            # print("bracket start %d,%d:%d" % (line_index, bracket_begin_pos, bracket_info.bracket_type))

            if bracket_begin_pos == len(line) - 1:
                return line_index + 1, 0
            else:
                return line_index, bracket_begin_pos + 1

        bracket_end_pos = line.find("}", pos)
        if bracket_end_pos > -1:
            # print("bracket end %d,%d:%d" % (line_index, bracket_begin_pos, len(self.bracket_stack)))

            bracket_info = self.bracket_stack.pop()
            if bracket_info.bracket_type == BracketInfo.Bracket_Namespace:
                if self.current_namespace:
                    self.current_namespace.end_line = line_index
                    if len(self.namespace_stack) > 0:
                        self.current_namespace = self.namespace_stack.pop()
                    else:
                        self.current_namespace = None
                else:
                    print("===>err! namespace is close before. current line %d" % line_index)

            elif bracket_info.bracket_type == BracketInfo.Bracket_Method:
                if self.current_method:
                    self.current_method.end_line = line_index
                    self.current_method = None
                else:
                    print("===>err! class is close before. current line %d" % line_index)

            if bracket_end_pos == len(line) - 1:
                return line_index + 1, 0
            else:
                return line_index, bracket_end_pos + 1

        return line_index + 1, 0

    def parse(self, lines):

        line_index = 0
        col = 0
        line_length = len(lines)
        while line_index < line_length:
            # print("parse line:%d" % line_index)
            line = lines[line_index].strip()

            if line:
                line_index, line = self._parse_comment(line, line_index, lines)

                if line:
                    line = self._parse_macro(line)
                    next_line_index, col = self._parse_namespace(line, line_index, lines, col)
                    if next_line_index == line_index:
                        next_line_index, col = self._parse_method(line, line_index, lines, col)

                        if next_line_index == line_index:
                            next_line_index, col = self._parse_bracket(line, line_index, lines, col)

                    line_index = next_line_index
                else:
                    line_index += 1
            else:
                line_index += 1
