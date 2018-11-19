import re
from parser_info import *


class ObjCFileParser:
    def __init__(self, macros=None):
        self.bracket_stack = []
        self.macros = macros

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
                line = line.search_replace(k, v)
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
        elif line.startswith("#define"):
            if line.endswith("\\"):
                line_index += 1
                while line_index < len(lines):
                    line = lines[line_index].strip()

                    line_index += 1
                    if not line.endswith("\\"):
                        break
            else:
                line_index += 1
        return line_index, line

    def _parse_line(self, line_index, lines):

        line = lines[line_index].strip()

        if line:
            line_index, line = self._parse_comment(line, line_index, lines)

            if line:
                line = self._parse_macro(line)

                line_index, line = self._parse_precompile(line, line_index, lines)

        return line_index, line


class ObjCHeadFileParser(ObjCFileParser):
    def __init__(self, macros=None):
        ObjCFileParser.__init__(self, macros)
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
        if not re.search(r'\s*@interface\s+', line):
            return line_index, pos

        class_pos = line.find("@interface", pos)
        if self._check_in_double_str(line, class_pos):
            return line_index, -1

        class_pos += len("@interface")
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
        class_name = segs[0]
        ext_pos = class_name.find("(")
        if ext_pos > -1:
            class_name = class_name[:ext_pos]

        print("find class name:%s" % class_name)

        parent_class = None
        if self.current_class:
            print "===>inner class find .name %s" % class_name
            self.class_stack.append(self.current_class)
            parent_class = self.current_class

        self.current_class = ClassInfo(class_name, None, line_index, parent_class)
        self.classes.append(self.current_class)

        if bracket_pos > -1:
            # create class bracket
            bracket_info = BracketInfo(line_index, bracket_pos + 1, BracketInfo.Bracket_Class)
            self.bracket_stack.append(bracket_info)
            self.current_class.bracket = bracket_info

            if bracket_pos == len(line) - 1:
                is_end_line = True
            else:
                is_end_line = False
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
                    if self.current_class and self.current_class.bracket is None:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Class)
                        self.current_class.bracket = bracket_info
                    else:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Other)

                    self.bracket_stack.append(bracket_info)

            elif c == "}":
                if not in_double_str and not in_single_str:
                    bracket_info = self.bracket_stack.pop()
                    bracket_info.end_line = line
                    bracket_info.end_col = i
                    # if bracket_info.bracket_type == BracketInfo.Bracket_Class:
                    #     if self.current_class:
                    #         self.current_class.end_line = line_index
                    #         if len(self.class_stack) > 0:
                    #             self.current_class = self.class_stack.pop()
                    #         else:
                    #             self.current_class = None
                    #     else:
                    #         print("===>err! class is close before. current line %d" % line_index)

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
            elif c == "@":

                if not in_double_str and not in_single_str:
                    if line[i:].startswith("end"):
                        # class define end
                        if self.current_class:
                            self.current_class.end_line = line_index
                            if len(self.class_stack) > 0:
                                self.current_class = self.class_stack.pop()
                            else:
                                self.current_class = None
                        else:
                            print("===>err! class is close before. current line %d" % line_index)

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
                        next_line_index, col = self._parse_class(line, line_index, lines, col)

                        if next_line_index == line_index:
                            next_line_index, col = self._parse_bracket(line, line_index, lines, col)

                    line_index = next_line_index
                else:
                    line_index += 1
            else:
                line_index += 1


class ObjCSourceFileParser(ObjCFileParser):
    def __init__(self, macros=None):
        ObjCFileParser.__init__(self, macros)
        self.classes = []
        self.class_stack = []
        self.current_class = None
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
        method_sign = line.find("-")
        if method_sign == -1:
            method_sign = line.find("+")

        if method_sign == -1:
            return line_index, pos

        if self._check_in_double_str(line, method_sign):
            return line_index, 0

        # remove return
        method_define = line[method_sign + 1:]
        method_pos = method_define.find("(", method_sign + 1)
        method_pos = method_define.find(")", method_pos + 1)
        method_define = method_define[method_pos + 1:]

        method_names = []
        method_pos = method_define.find(":")

        if method_pos > -1:
            method_names.append(method_define[:method_pos].strip())
            method_define = method_define[method_pos + 1:]
            method_pos = method_define.find(":")
            while method_pos > -1:
                segs = re.split("\s", method_define[:method_pos].strip())
                method_names.append(segs[-1])
                method_define = method_define[method_pos + 1:]
                method_pos = method_define.find(":")
        else:
            bracket_pos = method_define.find("{")
            if bracket_pos > -1:
                method_names.append(method_define[:bracket_pos].strip())
            else:
                method_names.append(method_define.strip())

        method_name = "_".join(method_names)
        if self.current_method:
            print "===>err method define not close %s::%s" % (self.current_method.class_name, self.current_method.name)
        else:
            if self.current_class:
                self.current_method = MethodInfo(method_name, self.current_class.name, line_index)
                self.methods.append(self.current_method)
            else:
                print "===>err method %s can't find class " % method_name

        bracket_pos = line.find("{", pos)
        if bracket_pos > -1:
            # create class bracket
            bracket_info = BracketInfo(line_index, bracket_pos + 1, BracketInfo.Bracket_Method)
            self.bracket_stack.append(bracket_info)
            self.current_method.bracket = bracket_info

            if bracket_pos == len(line) - 1:
                is_end_line = True
            else:
                is_end_line = False
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
                    if self.current_method and self.current_method.bracket is None:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Method)
                        self.current_method.bracket = bracket_info
                    else:
                        bracket_info = BracketInfo(line_index, i + 1, BracketInfo.Bracket_Other)

                    self.bracket_stack.append(bracket_info)

            elif c == "}":
                if not in_double_str and not in_single_str:
                    bracket_info = self.bracket_stack.pop()
                    if bracket_info.bracket_type == BracketInfo.Bracket_Method:
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

            elif c == "@":
                if not in_double_str and not in_single_str:
                    if line[i:].startswith("end"):
                        # class define end
                        if self.current_class:
                            self.current_class.end_line = line_index
                            if len(self.class_stack) > 0:
                                self.current_class = self.class_stack.pop()
                            else:
                                self.current_class = None
                        else:
                            print("===>err! class is close before. current line %d" % line_index)

        return line_index + 1, 0

    def _parse_class(self, line, line_index, lines, pos=0):
        # check have class
        if not re.search(r'\s*@implementation\s+', line):
            return line_index, pos

        class_pos = line.find("@implementation", pos)
        if self._check_in_double_str(line, class_pos):
            return line_index, -1

        class_pos += len("@implementation")
        # get class name
        class_define = line[class_pos:].strip()

        segs = class_define.split(" ")
        class_name = segs[0]
        ext_pos = class_name.find("(")
        if ext_pos > -1:
            class_name = class_name[:ext_pos]

        print("find class name:%s" % class_name)

        self.current_class = ClassInfo(class_name, None, line_index, None)
        self.classes.append(self.current_class)

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
                        next_line_index, col = self._parse_class(line, line_index, lines, col)

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

        return positions
