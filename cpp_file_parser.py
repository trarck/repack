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
    def __init__(self, class_name, namespace, start_line, parent_class=None):
        self.name = class_name
        self.namespace = namespace
        self.start_line = start_line
        self.end_line = -1
        # self.fields = []
        # self.methods = []
        self.bracket_start = None
        self.parent_class = parent_class


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

    def _check_in_double_str(self, line, pos):

        count = 0
        for i in range(0, pos):
            if line[i] == '"':
                count += 1
        if count % 2 == 1:
            return True
        else:
            return False

    def _parse_comment(self, line, line_index, lines):
        if line.startswith("//"):
            return line_index, None

        pos = line.find("//")
        if pos > 0:
            if self._check_in_double_str(line, pos):
                return line_index, line
            else:
                return line_index, line[:pos]

        pos = line.find("/*")
        if pos > -1:
            if self._check_in_double_str(line, pos):
                return line_index, line

            # print("find comment %d" % line_index)
            if pos > 0:
                new_line = line[:pos]
            else:
                new_line = None

            lines_count = len(lines)
            while True:

                pos = line.find("*/")

                # print("%s,%d:%d" % (line, line_index, pos))
                if pos > -1:
                    if self._check_in_double_str(line, pos):
                        return line_index, line

                    # print("find comment end %d" % line_index)
                    # print("%d:%d" % (pos + 2, len(line) - 1))
                    if pos + 2 < len(line) - 1:
                        if new_line:
                            new_line += line[pos:]
                        else:
                            new_line = line[pos:]
                    break
                line_index += 1
                if line_index >= lines_count:
                    print("out index %d" % line_index)
                    break

                line = lines[line_index].strip()

            return line_index, new_line

        return line_index, line

    def _parse_macro(self, line):
        if self.macros:
            for k, v in self.macros.items():
                line = line.replace(k, v)
        return line

    def _parse_precompile(self, line, line_index, lines):

        if line.startswith("#else"):
            # o_l = line_index
            line_index += 1
            if_wrap_count = 0

            while line_index < len(lines):
                line = lines[line_index].strip()

                if line.startswith("#endif"):
                    if if_wrap_count == 0:
                        return line_index + 1, None
                    else:
                        if_wrap_count -= 1

                elif line.startswith("#if"):
                    if_wrap_count += 1

                line_index += 1
            # print("in precompile end for %d" % o_l)

        return line_index, line

    def _parse_line(self, line_index, lines):

        line = lines[line_index].strip()

        if line:
            line_index, line = self._parse_comment(line, line_index, lines)

            if line:
                line = self._parse_macro(line)

                line_index, line = self._parse_precompile(line, line_index, lines)

        return line_index, line


class CppHeadFileParser(CppFileParser):
    def __init__(self, macros=None):
        CppFileParser.__init__(self, macros)
        self.classes = []
        self.class_stack = []
        self.current_class = None

    def _check_is_class_define(self, line, line_index, lines, pos):

        # enum class
        if line.startswith("enum"):
            return False

        # in template define
        if line[:pos].find("<") > -1:
            return False

        # predeclare
        pos = line.find(";", pos)
        if pos > -1:
            return False

        # class define
        pos = line.find("{")
        if pos > -1:
            return True

        # check next line
        lines_count = len(lines)
        line_index += 1
        while line_index < lines_count:
            line = lines[line_index].strip()
            if line:
                if line.find(";", pos) > -1:
                    return False
                elif line.find("{", pos) > -1:
                    return True

            line_index += 1

        raise "get class error"

    def _parse_class(self, line, line_index, lines, pos=0):
        # check have class
        if not re.search(r'\s*class\s+', line):
            return line_index, pos

        class_pos = line.find("class", pos)
        class_pos += len("class")
        if not self._check_is_class_define(line, line_index, lines, class_pos):
            # print("find class pre declare %d" % line_index)
            return line_index, 0

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
        if class_name == "final":
            class_name = segs[-2]
        print("find class name:%s" % class_name)

        parent_class = None
        if self.current_class:
            print "===>inner class find .name %s" % class_name
            self.class_stack.append(self.current_class)
            parent_class = self.current_class

        namespace_name = None
        if self.current_namespace:
            namespace_name = self.current_namespace.name
        self.current_class = ClassInfo(class_name, namespace_name, line_index, parent_class)
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

        line_count = len(line)
        in_double_str = False
        in_single_str = False
        for i in range(pos, line_count):
            c = line[i]
            if c == "{":
                if not in_double_str and not in_double_str:
                    if self.current_namespace and self.current_namespace.bracket_start is None:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Namespace)
                        self.current_namespace.bracket_start = bracket_info
                    elif self.current_class and self.current_class.bracket_start is None:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Class)
                        self.current_class.bracket_start = bracket_info
                    else:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Other)

                    self.bracket_stack.append(bracket_info)

            elif c == "}":
                if not in_double_str and not in_double_str:
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
                            if len(self.class_stack) > 0:
                                self.current_class = self.class_stack.pop()
                            else:
                                self.current_class = None
                        else:
                            print("===>err! class is close before. current line %d" % line_index)

            elif c == '"':
                if in_double_str:
                    in_double_str = False
                else:
                    # print("In double sting %d" % line_index)
                    in_double_str = True
            elif c == "'":
                if in_single_str:
                    in_single_str = False
                else:
                    # print("In single sting %d" % line_index)
                    in_single_str = True

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

                    next_line_index, line = self._parse_precompile(line, line_index, lines)
                    if next_line_index == line_index:
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

        if re.match(r'(if|for|while)\s*\(', line):
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

                    if re.match(r'(if|for|while)\s*\(', line):
                        return False

            line_index += 1

    def _parse_method(self, line, line_index, lines, pos=0):
        # check have class
        m = re.search(r'\s*(.*)::(.*)\s*\(', line)
        if not m:
            return line_index, pos

        class_name = re.split("\s", m.group(1))[-1]
        method_name = m.group(2)

        method_pos = line.find(class_name + "::" + method_name, pos)
        if not self._check_is_function_define(line, line_index, lines, method_pos):
            # print("find function call %d" % line_index)
            return line_index + 1, 0

        # get class name

        # print("find method name:%s::%s" % (class_name, method_name))

        if self.current_method:
            print "===>err method define not close %s::%s" % (self.current_method.class_name, self.current_method.name)
        else:
            self.current_method = MethodInfo(method_name, class_name, line_index)
            self.methods.append(self.current_method)

        bracket_pos = line.find("{", method_pos)
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

        line_count = len(line)
        in_double_str = False
        in_single_str = False
        for i in range(pos, line_count):
            c = line[i]
            if c == "{":
                if not in_double_str and not in_single_str:
                    if self.current_namespace and self.current_namespace.bracket_start is None:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Namespace)
                        self.current_namespace.bracket_start = bracket_info
                    elif self.current_method and self.current_method.bracket_start is None:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Method)
                        self.current_method.bracket_start = bracket_info
                    else:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Other)

                    self.bracket_stack.append(bracket_info)

            elif c == "}":
                if not in_double_str and not in_single_str:
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

            elif c == '"':
                if in_double_str:
                    in_double_str = False
                else:
                    # print("In double sting %d" % line_index)
                    in_double_str = True

            elif c == "'":

                if in_single_str:
                    in_single_str = False
                else:
                    # print("In single sting %d" % line_index)
                    in_single_str = True

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
                    next_line_index, line = self._parse_precompile(line, line_index, lines)
                    if next_line_index == line_index:
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

    def get_method_inject_positions(self, method_info, lines):
        positions = []
        sign = 0
        for line_index in range(method_info.start_line, method_info.end_line):
            line_index, line = self._parse_line(line_index, lines)
            if line:
                if line.endswith(";"):
                    sign += 1
                else:
                    sign = 0

                if sign >= 2:
                    sign = 0
                    positions.append(line_index)
            else:
                line_index += 1
        print("method:%s" % method_info.name)
        print(positions)
        return positions
