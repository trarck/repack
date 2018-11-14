import os
import shutil
import random

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
chars_length = len(chars)

words_file_path = os.path.join(os.path.dirname(__file__), "data/words.txt")
fp = open(words_file_path)
words = fp.readlines()
fp.close()
words_length = len(words)
for i in range(words_length):
    words[i] = words[i].strip()


class RandomGenerater:
    @staticmethod
    def generate_name(min_length=6, max_length=64):
        length = random.randint(min_length, max_length)
        return ''.join(chars[random.randint(0, chars_length - 1)] for _ in range(length))

    @staticmethod
    def generate_name_first_upper(min_length=6, max_length=64):
        name = RandomGenerater.generate_name(min_length, max_length)
        return name[0].upper() + name[1:]

    @staticmethod
    def generate_name_first_lower(min_length=6, max_length=64):
        name = RandomGenerater.generate_name(min_length, max_length)
        return name[0].lower() + name[1:]

    @staticmethod
    def generate_int(max_value=999999):
        return random.randint(0, max_value)

    @staticmethod
    def generate_float(max_value=999999):
        return random.uniform(0, max_value)

    @staticmethod
    def generate_string(min_length=6, max_length=64):
        return RandomGenerater.generate_name(min_length, max_length)

    @staticmethod
    def get_reandom_indexs(size, count,start_index=1):
        indexs = range(size)
        for i in range(count):
            index = random.randint(start_index, size - 1 - i)
            t = indexs[index]
            indexs[index] = indexs[-1 - i]
            indexs[-1 - i] = t
        return indexs[-count:]

    @staticmethod
    def random_split(arr,split_count):
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
    def generate_words(min_count=2, max_count=5, join_str=None,max_join_count=0):
        length = random.randint(min_count, max_count)
        if join_str is None:
            return ''.join(words[random.randint(0, words_length - 1)] for _ in range(length))
        else:
            s = []
            for _ in range(length):
                w = words[random.randint(0, words_length - 1)]
                s.append(w[0].upper() + w[1:])
            if max_join_count > 0:
                join_count = random.randint(1, max_join_count)
                if join_count < length:
                    subs=RandomGenerater.random_split(s,join_count)
                    return join_str.join(subs)
            return join_str.join(s)

    @staticmethod
    def generate_words_first_upper(min_count=2, max_count=5, join_str=None,max_join_count=0):
        length = random.randint(min_count, max_count)
        s = []
        for _ in range(length):
            w = words[random.randint(0, words_length - 1)]
            s.append(w[0].upper() + w[1:])
        if join_str is None:
            return ''.join(s)
        else:
            if max_join_count > 0:
                join_count = random.randint(1, max_join_count)
                if join_count < length:
                    subs=RandomGenerater.random_split(s,join_count)
                    return join_str.join(subs)

            return join_str.join(s)

    @staticmethod
    def generate_words_first_lower(min_count=2, max_count=5, join_str=None, max_join_count=0):
        length = random.randint(min_count, max_count)
        s = []
        for _ in range(length):
            w = words[random.randint(0, words_length - 1)]
            s.append(w[0].lower() + w[1:])
        if join_str is None:
            return ''.join(s)
        else:
            if max_join_count > 0:
                join_count = random.randint(1, max_join_count)
                if join_count < length:
                    subs=RandomGenerater.random_split(s,join_count)
                    return join_str.join(subs)
            return join_str.join(s)
