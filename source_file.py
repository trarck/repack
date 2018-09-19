class SourceFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = None

    def open(self):
        fp = open(self.file_path, 'r')
        self.content = fp.read().decode("utf-8")
        fp.close()

    def save(self):
        fp = open(self.file_path, 'w')
        fp.write(self.content.encode("utf-8"))
        fp.close()

    def insert(self, keys, words):
        pos = 0
        for k in keys:
            pos = self.content.find(k, pos)
            if pos == -1:
                return False
            pos += len(k)
        self.content = self.content[:pos] + words + self.content[pos:]

    def insert_before(self, keys, words):
        pos = 0
        next_pos = 0
        for k in keys:
            pos = self.content.find(k, next_pos)
            if pos == -1:
                return False
            next_pos = pos + len(k)
        self.content = self.content[:pos] + words + self.content[pos:]

    def replace(self, froms, tos, words):
        from_pos = 0
        from path_crypt import PathCrypt
        # print(PathCrypt.byte_to_hex(self.content))
        # self.content=self.content.decode("utf-8")
        # print(PathCrypt.byte_to_hex(self.content))
        for k in froms:
            print(self.content)
            from_pos = self.content.find(k, from_pos)
            if from_pos == -1:
                return False
            from_pos += len(k)

        to_pos = 0
        find_next_pos = from_pos
        for k in tos:
            to_pos = self.content.find(k, find_next_pos)
            if to_pos == -1:
                return False
            find_next_pos = to_pos + len(k)
        self.content = self.content[:from_pos] + words + self.content[to_pos:]

    def replace_after(self, froms, tos, words):
        from_pos = 0
        for k in froms:
            from_pos = self.content.find(k, from_pos)
            if from_pos == -1:
                return False
            from_pos += len(k)

        to_pos = from_pos

        for k in tos:
            to_pos = self.content.find(k, to_pos)
            if to_pos == -1:
                return False
            to_pos += len(k)
        self.content = self.content[:from_pos] + words + self.content[to_pos:]

    def remove(self, froms, tos):
        from_pos = 0
        for k in froms:
            from_pos = self.content.find(k, from_pos)
            if from_pos == -1:
                return False
            from_pos += len(k)

        to_pos = 0
        find_next_pos = from_pos
        for k in tos:
            to_pos = self.content.find(k, find_next_pos)
            if to_pos == -1:
                return False
            find_next_pos = to_pos + len(k)
        self.content = self.content[:from_pos] + self.content[to_pos:]