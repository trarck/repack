import random
import os

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
chars_length = len(chars)

cpp_types = ["int", "long long", "float", "double", "std::string"]
cpp_types_length = len(cpp_types)

objc_types = ["NSInteger", "CGFloat", "NSString*"]
objc_types_length = len(objc_types)


class WordsManager:
    words = []
    words_length = 0

    class_words = []
    class_words_length = 0

    filed_words = []
    filed_words_length = 0

    function_words = []
    function_words_length = 0

    @staticmethod
    def init_words():
        words_file_path = os.path.join(os.path.dirname(__file__), "data/words.txt")
        WordsManager.load_words(words_file_path)

        words_file_path = os.path.join(os.path.dirname(__file__), "data/class_words.txt")
        if os.path.exists(words_file_path):
            WordsManager.load_class_words(words_file_path)

        words_file_path = os.path.join(os.path.dirname(__file__), "data/field_words.txt")
        if os.path.exists(words_file_path):
            WordsManager.load_field_words(words_file_path)

        words_file_path = os.path.join(os.path.dirname(__file__), "data/function_words.txt")
        if os.path.exists(words_file_path):
            WordsManager.load_function_words(words_file_path)

    @staticmethod
    def load_words(words_file_path):
        if os.path.exists(words_file_path):
            fp = open(words_file_path)
            ws = fp.readlines()
            fp.close()
            for w in ws:
                word = w.strip()
                if word:
                    WordsManager.words.append(word)
                    WordsManager.words_length += 1

    @staticmethod
    def load_class_words(words_file_path):
        if os.path.exists(words_file_path):
            fp = open(words_file_path)
            ws = fp.readlines()
            fp.close()
            for w in ws:
                word = w.strip()
                if word:
                    WordsManager.class_words.append(word)
                    WordsManager.class_words_length += 1

    @staticmethod
    def load_field_words(words_file_path):
        if os.path.exists(words_file_path):
            fp = open(words_file_path)
            ws = fp.readlines()
            fp.close()
            for w in ws:
                word = w.strip()
                if word:
                    WordsManager.filed_words.append(word)
                    WordsManager.filed_words_length += 1

    @staticmethod
    def load_function_words(words_file_path):
        if os.path.exists(words_file_path):
            fp = open(words_file_path)
            ws = fp.readlines()
            fp.close()
            for w in ws:
                word = w.strip()
                if word:
                    WordsManager.function_words.append(word)
                    WordsManager.function_words_length += 1

    @staticmethod
    def clean_all():
        WordsManager.words = []
        WordsManager.words_length = 0

        WordsManager.class_words = []
        WordsManager.class_words_length = 0

        WordsManager.filed_words = []
        WordsManager.filed_words_length = 0

        WordsManager.function_words = []
        WordsManager.function_words_length = 0

    @staticmethod
    def clean_all():
        WordsManager.words = []
        WordsManager.words_length = 0

        WordsManager.class_words = []
        WordsManager.class_words_length = 0

        WordsManager.filed_words = []
        WordsManager.filed_words_length = 0

        WordsManager.function_words = []
        WordsManager.function_words_length = 0

    @staticmethod
    def clean_words():
        WordsManager.words = []
        WordsManager.words_length = 0

    @staticmethod
    def clean_class_words():
        WordsManager.class_words = []
        WordsManager.class_words_length = 0

    @staticmethod
    def clean_filed_words():
        WordsManager.filed_words = []
        WordsManager.filed_words_length = 0

    @staticmethod
    def clean_function_words():
        WordsManager.function_words = []
        WordsManager.function_words_length = 0


class RandomGenerater:
    @staticmethod
    def upper_first(s):
        return s[0].upper() + s[1:]

    @staticmethod
    def lower_first(s):
        return s[0].lower() + s[1:]

    @staticmethod
    def generate_int(max_value=10000):
        return random.randint(0, max_value)

    @staticmethod
    def generate_float(max_value=10000):
        return random.uniform(0, max_value)

    @staticmethod
    def generate_string(min_length=6, max_length=64):
        length = random.randint(min_length, max_length)
        return ''.join(chars[random.randint(0, chars_length - 1)] for _ in range(length))

    @staticmethod
    def generate_string_first_upper(min_length=6, max_length=64):
        name = RandomGenerater.generate_string(min_length, max_length)
        return name[0].upper() + name[1:]

    @staticmethod
    def generate_string_first_lower(min_length=6, max_length=64):
        name = RandomGenerater.generate_string(min_length, max_length)
        return name[0].lower() + name[1:]

    @staticmethod
    def generate_key():
        return ''.join(chr(random.randrange(ord('a'), ord('z'))) for _ in range(16))

    @staticmethod
    def get_reandom_indexs(size, count, start_index=1):
        indexs = range(size)
        for i in range(count):
            index = random.randint(start_index, size - 1 - i)
            t = indexs[index]
            indexs[index] = indexs[-1 - i]
            indexs[-1 - i] = t
        return indexs[-count:]

    @staticmethod
    def random_split(arr, split_count):
        indexs = RandomGenerater.get_reandom_indexs(len(arr), split_count)
        last_index = 0
        subs = []
        indexs.sort()
        for i in range(split_count):
            index = indexs[i]
            subs.append(''.join(arr[last_index:index]))
            last_index = index
        subs.append(''.join(arr[last_index:]))
        return subs

    @staticmethod
    def generate_words(min_count=2, max_count=5, join_str=None, max_join_count=0):
        length = random.randint(min_count, max_count)
        if join_str is None:
            return ''.join(WordsManager.words[random.randint(0, WordsManager.words_length - 1)] for _ in range(length))
        else:
            s = []
            for _ in range(length):
                w = WordsManager.words[random.randint(0, WordsManager.words_length - 1)]
                s.append(w[0].upper() + w[1:])
            if max_join_count > 0:
                join_count = random.randint(1, max_join_count)
                if join_count < length:
                    subs = RandomGenerater.random_split(s, join_count)
                    return join_str.join(subs)
            return join_str.join(s)

    @staticmethod
    def generate_words_first_upper(min_count=2, max_count=5, join_str=None, max_join_count=0):
        length = random.randint(min_count, max_count)
        s = []
        for _ in range(length):
            w = WordsManager.words[random.randint(0, WordsManager.words_length - 1)]
            s.append(w[0].upper() + w[1:])
        if join_str is None:
            return ''.join(s)
        else:
            if max_join_count > 0:
                join_count = random.randint(1, max_join_count)
                if join_count < length:
                    subs = RandomGenerater.random_split(s, join_count)
                    return join_str.join(subs)

            return join_str.join(s)

    @staticmethod
    def generate_words_first_lower(min_count=2, max_count=5, join_str=None, max_join_count=0):
        length = random.randint(min_count, max_count)
        s = []
        for _ in range(length):
            w = WordsManager.words[random.randint(0, WordsManager.words_length - 1)]
            s.append(w[0].lower() + w[1:])
        if join_str is None:
            return ''.join(s)
        else:
            if max_join_count > 0:
                join_count = random.randint(1, max_join_count)
                if join_count < length:
                    subs = RandomGenerater.random_split(s, join_count)
                    return join_str.join(subs)
            return join_str.join(s)

    @staticmethod
    def generate_words_with_random_prev_tail(min_prev_length=2, max_prev_length=3, min_tail_length=2, max_tail_lenth=3,
                                             min_word_length=3, max_word_length=6):
        name = RandomGenerater.generate_string(min_prev_length, max_prev_length)

        name += RandomGenerater.generate_words(min_word_length, max_word_length)

        name += RandomGenerater.generate_string(min_tail_length, max_tail_lenth)
        return name

    @staticmethod
    def generate_cpp_type():
        return cpp_types[random.randint(0, cpp_types_length - 1)]

    @staticmethod
    def generate_value(type_name):
        if type_name == "NSInteger" or type_name == "int" or type_name == "long long":
            return RandomGenerater.generate_int()
        elif type_name == "CGFloat" or type_name == "float" or type_name == "double":
            return RandomGenerater.generate_float()
        else:
            return RandomGenerater.generate_string()

    @staticmethod
    def generate_value_stringify(type_name):
        if type_name == "NSInteger" or type_name == "int" or type_name == "long long":
            return str(RandomGenerater.generate_int())
        elif type_name == "CGFloat" or type_name == "float" or type_name == "double":
            return str(RandomGenerater.generate_float())
        elif type_name.startswith("NSString"):
            return "@\"%s\"" % RandomGenerater.generate_string()
        else:
            return "\"%s\"" % RandomGenerater.generate_string()

    @staticmethod
    def generate_objc_type():
        return objc_types[random.randint(0, objc_types_length - 1)]
