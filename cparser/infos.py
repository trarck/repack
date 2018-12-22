from clang import cindex
import re
import utils


class TypeInfo(object):
    def __init__(self, cursor=None):
        self.cursor = cursor
        self.is_object = False
        self.is_function = False
        self.is_enum = False
        self.is_numeric = False
        self.is_const = False
        self.is_pointer = False
        self.not_supported = False
        self.param_types = []
        self.ret_type = None
        self.fullname = ""  # with namespace and class name
        self.namespace_name = ""  # only contains namespace
        self.name = ""
        self.whole_name = None
        self.canonical_type = None

    @staticmethod
    def from_type(type_cursor):
        if type_cursor.kind == cindex.TypeKind.POINTER:
            nt = TypeInfo.from_type(type_cursor.get_pointee())

            if None != nt.canonical_type:
                nt.canonical_type.name += "*"
                nt.canonical_type.fullname += "*"
                nt.canonical_type.whole_name += "*"

            nt.name += "*"
            nt.fullname += "*"
            nt.whole_name = nt.fullname
            nt.is_enum = False
            nt.is_const = type_cursor.get_pointee().is_const_qualified()
            nt.is_pointer = True
            if nt.is_const:
                nt.whole_name = "const " + nt.whole_name
        elif type_cursor.kind == cindex.TypeKind.LVALUEREFERENCE:
            nt = TypeInfo.from_type(type_cursor.get_pointee())
            nt.is_const = type_cursor.get_pointee().is_const_qualified()
            nt.whole_name = nt.whole_name + "&"

            if nt.is_const:
                nt.whole_name = "const " + nt.whole_name

            if None != nt.canonical_type:
                nt.canonical_type.whole_name += "&"
        else:
            nt = TypeInfo(type_cursor)
            decl = type_cursor.get_declaration()

            nt.fullname = utils.get_fullname(decl).replace('::__ndk1', '')

            if decl.kind == cindex.CursorKind.CLASS_DECL \
                    and not nt.fullname.startswith('std::function') \
                    and not nt.fullname.startswith('std::string') \
                    and not nt.fullname.startswith('std::basic_string'):
                nt.is_object = True
                displayname = decl.displayname.replace('::__ndk1', '')
                nt.name = utils.normalize_type_str(displayname)
                nt.fullname = utils.normalize_type_str(nt.fullname)
                nt.namespace_name = utils.get_namespace_name(decl)
                nt.whole_name = nt.fullname
            else:
                if decl.kind == cindex.CursorKind.NO_DECL_FOUND:
                    nt.name = utils.native_name_from_type(type_cursor)
                else:
                    nt.name = decl.spelling
                nt.namespace_name = utils.get_namespace_name(decl)

                if len(nt.fullname) > 0:
                    nt.fullname = utils.normalize_type_str(nt.fullname)

                if nt.fullname.startswith("std::function"):
                    nt.name = "std::function"

                if len(nt.fullname) == 0 or nt.fullname.find("::") == -1:
                    nt.fullname = nt.name

                nt.whole_name = nt.fullname
                nt.is_const = type_cursor.is_const_qualified()
                if nt.is_const:
                    nt.whole_name = "const " + nt.whole_name

                # Check whether it's a std::function typedef
                cdecl = type_cursor.get_canonical().get_declaration()
                if None != cdecl.spelling and 0 == cmp(cdecl.spelling, "function"):
                    nt.name = "std::function"

                if nt.name != utils.INVALID_NATIVE_TYPE and nt.name != "std::string" and nt.name != "std::function":
                    if type_cursor.kind == cindex.TypeKind.UNEXPOSED or type_cursor.kind == cindex.TypeKind.TYPEDEF or type_cursor.kind == cindex.TypeKind.ELABORATED:
                        ret = TypeInfo.from_type(type_cursor.get_canonical())
                        if ret.name != "":
                            if decl.kind == cindex.CursorKind.TYPEDEF_DECL:
                                ret.canonical_type = nt
                            return ret

                nt.is_enum = type_cursor.get_canonical().kind == cindex.TypeKind.ENUM

                if nt.name == "std::function":
                    nt.is_object = False
                    lambda_display_name = utils.get_fullname(cdecl)
                    lambda_display_name = lambda_display_name.replace("::__ndk1", "")
                    lambda_display_name = utils.normalize_type_str(lambda_display_name)
                    nt.fullname = lambda_display_name
                    r = re.compile('function<([^\s]+).*\((.*)\)>').search(nt.fullname)
                    (ret_type, params) = r.groups()
                    params = filter(None, params.split(", "))

                    nt.is_function = True
                    nt.ret_type = TypeInfo.from_string(ret_type)
                    nt.param_types = [TypeInfo.from_string(string) for string in params]

        # mark argument as not supported
        if nt.name == utils.INVALID_NATIVE_TYPE:
            nt.not_supported = True

        if re.search("(short|int|double|float|long|size_t)$", nt.name) is not None:
            nt.is_numeric = True

        return nt

    @staticmethod
    def from_string(displayname):
        displayname = displayname.replace(" *", "*")

        nt = TypeInfo()
        nt.name = displayname.split("::")[-1]
        nt.fullname = displayname
        nt.whole_name = nt.fullname
        nt.is_object = True
        return nt

    @property
    def lambda_parameters(self):
        params = ["%s larg%d" % (str(nt), i) for i, nt in enumerate(self.param_types)]
        return ", ".join(params)

    def __str__(self):
        return self.canonical_type.whole_name if None != self.canonical_type else self.whole_name


class FieldAttributes(object):
    Empty = 0
    Private = 1
    Protected = 2
    Public = 3

    BaseAttributeEnd = 15

    Static = 16


class FieldInfo(object):
    def __init__(self, cursor):
        cursor = cursor.canonical
        self.cursor = cursor
        self.name = cursor.displayname
        self.kind = cursor.type.kind
        self.location = cursor.location

        self.signature_name = self.name
        self.field_type = TypeInfo.from_type(cursor.type)
        self.attributes = FieldAttributes.Empty

        if self.cursor.access_specifier == cindex.AccessSpecifier.PRIVATE:
            self.set_attribute(FieldAttributes.Private)
        elif self.cursor.access_specifier == cindex.AccessSpecifier.PROTECTED:
            self.set_attribute(FieldAttributes.Protected)
        elif self.cursor.access_specifier == cindex.AccessSpecifier.PUBLIC:
            self.set_attribute(FieldAttributes.Public)

    def set_attribute(self, value):
        if value > FieldAttributes.BaseAttributeEnd:
            self.attributes = self.attributes | value
        else:
            self.attributes = (self.attributes ^ (self.attributes & FieldAttributes.BaseAttributeEnd)) | value

    @property
    def is_private(self):
        return self.attributes & FieldAttributes.BaseAttributeEnd == FieldAttributes.Private

    @property
    def is_protected(self):
        return self.attributes & FieldAttributes.BaseAttributeEnd == FieldAttributes.Protected

    @property
    def is_public(self):
        return self.attributes & FieldAttributes.BaseAttributeEnd == FieldAttributes.Public

    @property
    def is_static(self):
        return self.attributes & FieldAttributes.Static > 0

    @staticmethod
    def can_parse(type_cursor):
        native_type = TypeInfo.from_type(type_cursor)
        if type_cursor.kind == cindex.TypeKind.UNEXPOSED and native_type.name != "std::string":
            return False
        return True


class FunctionAttributes(object):
    Empty = 0
    Private = 1
    Protected = 2
    Public = 3

    BaseAttributeEnd = 15
    Static = 16
    Final = 32
    Virtual = 64
    Constructor = 128
    Destructor = 256
    Const = 512
    Implement = 1024


class FunctionInfo(object):
    def __init__(self, cursor):
        self.cursor = cursor
        self.func_name = cursor.spelling
        self.signature_name = self.func_name
        self.arguments = []
        self.argumentTips = []
        self.implementations = []
        self.is_overloaded = False
        self.is_constructor = False
        self.not_supported = False
        self.is_override = False
        self.ret_type = TypeInfo.from_type(cursor.result_type)
        self.comment = self.get_comment(cursor.raw_comment)
        self.attributes = FunctionAttributes.Empty
        self.class_name = None

        self._parse()

    def _parse(self):
        # parse the arguments

        for arg in self.cursor.get_arguments():
            self.argumentTips.append(arg.spelling)
            nt = TypeInfo.from_type(arg.type)
            self.arguments.append(nt)
            # mark the function as not supported if at least one argument is not supported
            if nt.not_supported:
                self.not_supported = True

        found_default_arg = False
        index = -1

        for arg_node in self.cursor.get_children():
            if arg_node.kind == cindex.CursorKind.CXX_OVERRIDE_ATTR:
                self.is_override = True
            if arg_node.kind == cindex.CursorKind.PARM_DECL:
                index += 1
                if utils.iterate_param_node(arg_node):
                    found_default_arg = True
                    break

        self.min_args = index if found_default_arg else len(self.arguments)

        # set access specifier
        if self.cursor.access_specifier == cindex.AccessSpecifier.PRIVATE:
            self.set_attribute(FunctionAttributes.Private)
        elif self.cursor.access_specifier == cindex.AccessSpecifier.PROTECTED:
            self.set_attribute(FunctionAttributes.Protected)
        elif self.cursor.access_specifier == cindex.AccessSpecifier.PUBLIC:
            self.set_attribute(FunctionAttributes.Public)

        # check is static function
        if self.cursor.is_static_method():
            self.set_attribute(FunctionAttributes.Static)

        # check is virtual function
        if self.cursor.is_virtual_method():
            self.set_attribute(FunctionAttributes.Virtual)

        if self.cursor.is_const_method():
            self.set_attribute(FunctionAttributes.Const)

        # set class name
        if self.cursor.semantic_parent.kind == cindex.CursorKind.CLASS_DECL \
                or self.cursor.semantic_parent.kind == cindex.CursorKind.OBJC_INTERFACE_DECL \
                or self.cursor.semantic_parent.kind == cindex.CursorKind.OBJC_CATEGORY_DECL:
            self.class_name = utils.get_fullname(self.cursor.semantic_parent)

        # check have implement
        if self._check_have_implement():
            self.set_attribute(FunctionAttributes.Implement)

    def _check_have_implement(self):
        have_implement = False

        for node in self.cursor.get_children():
            if node.kind == cindex.CursorKind.COMPOUND_STMT:
                have_implement = True
                break
        return have_implement

    def get_comment(self, comment):
        replace_str = comment

        if comment is None:
            return ""

        regular_replace_list = [
            ("(\s)*//!", ""),
            ("(\s)*//", ""),
            ("(\s)*/\*\*", ""),
            ("(\s)*/\*", ""),
            ("\*/", ""),
            ("\r\n", "\n"),
            ("\n(\s)*\*", "\n"),
            ("\n(\s)*@", "\n"),
            ("\n(\s)*", "\n"),
            ("\n(\s)*\n", "\n"),
            ("^(\s)*\n", ""),
            ("\n(\s)*$", ""),
            ("\n", "<br>\n"),
            ("\n", "\n-- ")
        ]

        for item in regular_replace_list:
            replace_str = re.sub(item[0], item[1], replace_str)

        return replace_str

    def set_attribute(self, value):
        if value > FunctionAttributes.BaseAttributeEnd:
            self.attributes = self.attributes | value
        else:
            self.attributes = (self.attributes ^ (self.attributes & FunctionAttributes.BaseAttributeEnd)) | value

    @property
    def is_private(self):
        return self.attributes & FunctionAttributes.BaseAttributeEnd == FunctionAttributes.Private

    @property
    def is_protected(self):
        return self.attributes & FunctionAttributes.BaseAttributeEnd == FunctionAttributes.Protected

    @property
    def is_public(self):
        return self.attributes & FunctionAttributes.BaseAttributeEnd == FunctionAttributes.Public

    @property
    def is_static(self):
        return self.attributes & FunctionAttributes.Static > 0

    @property
    def is_virtual(self):
        return self.attributes & FunctionAttributes.Virtual > 0

    @property
    def is_const(self):
        return self.attributes & FunctionAttributes.Const > 0

    @property
    def is_implement(self):
        return self.attributes & FunctionAttributes.Implement > 0

    def get_extent_start(self):
        if self.cursor is not None:
            return self.cursor.extent.start
        else:
            return None

    def get_extent_start_line(self):
        if self.cursor is not None:
            return self.cursor.extent.start.line
        else:
            return -1

    def get_extent_end(self):
        if self.cursor is not None:
            return self.cursor.extent.end
        else:
            return None

    def get_extent_end_line(self):
        if self.cursor is not None:
            return self.cursor.extent.end.line
        else:
            return -1


class ClassInfo(object):
    def __init__(self, cursor):
        # the cursor to the implementation
        self.cursor = cursor
        self.class_name = cursor.displayname
        self.is_ref_class = self.class_name == "Ref"
        self.full_class_name = self.class_name
        self.parents = []
        self.fields = []
        self.public_fields = []
        self.static_fields = []
        self.methods = []
        self.is_abstract = False  # self.class_name in generator.abstract_classes
        self._current_visibility = cindex.AccessSpecifier.PRIVATE
        # for generate lua api doc
        self.override_methods = {}
        self.has_constructor = False
        self.namespace_name = ""

        self.full_class_name = utils.get_fullname(cursor)
        self.namespace_name = utils.get_namespace_name(cursor)

        self._parse()

    @property
    def underlined_class_name(self):
        return self.full_class_name.replace("::", "_")

    def _parse(self):
        """
        parse the current cursor, getting all the necesary information
        """
        # the root cursor is CLASS_DECL.
        for cursor in self.cursor.get_children():
            self._traverse(cursor)

    def methods_clean(self):
        """
        clean list of methods (without the ones that should be skipped)
        """
        ret = []
        for name, impl in self.methods.iteritems():
            should_skip = False
            if name == 'constructor':
                should_skip = True
            else:
                if self.generator.should_skip(self.class_name, name):
                    should_skip = True
            if not should_skip:
                ret.append({"name": name, "impl": impl})
        return ret

    def override_methods_clean(self):
        """
        clean list of override methods (without the ones that should be skipped)
        """
        ret = []
        for name, impl in self.override_methods.iteritems():
            should_skip = self.generator.should_skip(self.class_name, name)
            if not should_skip:
                ret.append({"name": name, "impl": impl})
        return ret

    def _traverse(self, cursor=None, depth=0):
        if cursor.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
            parent = cursor.get_definition()
            parent_name = parent.displayname

            # if not self.class_name in self.generator.classes_have_no_parents:
            #     if parent_name and parent_name not in self.generator.base_classes_to_skip:
            #         # if parent and self.generator.in_listed_classes(parent.displayname):
            #         if not self.generator.parsed_classes.has_key(parent.displayname):
            #             parent = NativeClass(parent, self.generator)
            #             self.generator.parsed_classes[parent.class_name] = parent
            #         else:
            #             parent = self.generator.parsed_classes[parent.displayname]
            #
            #         self.parents.append(parent)
            #
            # if parent_name == "Ref":
            #     self.is_ref_class = True

        elif cursor.kind == cindex.CursorKind.FIELD_DECL:
            self.fields.append(FieldInfo(cursor))
            if self._current_visibility == cindex.AccessSpecifier.PUBLIC and FieldInfo.can_parse(cursor.type):
                self.public_fields.append(FieldInfo(cursor))
        elif cursor.kind == cindex.CursorKind.VAR_DECL:
            self.static_fields.append(FieldInfo(cursor))
        elif cursor.kind == cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
            self._current_visibility = cursor.access_specifier
        elif cursor.kind == cindex.CursorKind.CXX_METHOD:  # and cursor.availability != cindex.AvailabilityKind.DEPRECATED:
            # skip if variadic
            m = FunctionInfo(cursor)
            registration_name = m.func_name  # self.generator.should_rename_function(self.class_name, m.func_name) or m.func_name
            # bail if the function is not supported (at least one arg not supported)
            if m.not_supported:
                return None

            self.methods.append(m)
        elif cursor.kind == cindex.CursorKind.CONSTRUCTOR and not self.is_abstract:
            # Skip copy constructor
            if cursor.displayname == self.class_name + "(const " + self.full_class_name + " &)":
                # print "Skip copy constructor: " + cursor.displayname
                return None

            m = FunctionInfo(cursor)
            m.is_constructor = True
            m.set_attribute(FunctionAttributes.Constructor)
            self.has_constructor = True
            self.methods.append(m)
        elif cursor.kind == cindex.CursorKind.DESTRUCTOR:
            m = FunctionInfo(cursor)
            m.set_attribute(FunctionAttributes.Destructor)
            self.methods.append(m)
        # else:
        #     print "unknown cursor: %s - %s" % (cursor.kind, cursor.displayname)

    @staticmethod
    def _is_method_in_parents(current_class, method_name):
        if len(current_class.parents) > 0:
            if method_name in current_class.parents[0].methods:
                return True
            return ClassInfo._is_method_in_parents(current_class.parents[0], method_name)
        return False

    def _is_ref_class(self, depth=0):
        """
        Mark the class as 'cocos2d::Ref' or its subclass.
        """
        # print ">" * (depth + 1) + " " + self.class_name

        for parent in self.parents:
            if parent._is_ref_class(depth + 1):
                return True

        if self.is_ref_class:
            return True

        return False


class NamespaceInfo(object):
    def __init__(self, cursor):
        self.cursor = cursor


class ObjcProperty(object):
    def __init__(self, cursor):
        self.cursor = cursor
        self.name = cursor.displayname
        self.kind = cursor.type.kind
        self.location = cursor.location

        self.signature_name = self.name
        self.field_type = TypeInfo.from_type(cursor.type)


class ObjcClassInfo(ClassInfo):
    def __init__(self, cursor):
        self.properties = []
        self.is_category = False
        self.associated_class = None
        self.associated_class_displayname = None
        super(ObjcClassInfo, self).__init__(cursor)

    def _traverse(self, cursor=None, depth=0):
        super(ObjcClassInfo, self)._traverse(cursor, depth)
        # objc desc
        if cursor.kind == cindex.CursorKind.OBJC_IVAR_DECL:
            self.fields.append(FieldInfo(cursor))
        elif cursor.kind == cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL:
            m = FunctionInfo(cursor)
            self.methods.append(m)
        elif cursor.kind == cindex.CursorKind.OBJC_CLASS_METHOD_DECL:
            m = FunctionInfo(cursor)
            m.set_attribute(FunctionAttributes.Static)
            self.methods.append(m)
        elif cursor.kind == cindex.CursorKind.OBJC_PROPERTY_DECL:
            print("do nothing OBJC_PROPERTY_DECL")
            p = ObjcProperty(cursor)
            self.properties.append(p)
        elif cursor.kind == cindex.CursorKind.OBJC_CLASS_REF:
            self.associated_class_displayname = cursor.displayname
        else:
            print "unknown cursor: %s - %s" % (cursor.kind, cursor.displayname)
