class NamespaceInfo:
    def __init__(self, name, start_line, parent_name=None):
        self.name = name
        self.start_line = start_line
        self.end_line = -1
        self.bracket = None
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
        self.end_line = -1
        self.end_col = -1


class ClassInfo:
    def __init__(self, class_name, namespace, start_line, parent_class=None):
        self.name = class_name
        self.namespace = namespace
        self.start_line = start_line
        self.end_line = -1
        # self.fields = []
        # self.methods = []
        self.bracket = None
        self.parent_class = parent_class


class MethodInfo:
    def __init__(self, name, class_name, start_line):
        self.name = name
        self.class_name = class_name
        self.start_line = start_line
        self.end_line = -1
        self.bracket = None
