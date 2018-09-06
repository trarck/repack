import os;
import md5


class PathCrypt:
    @staticmethod
    def byte_to_hex(byte_str):
        """
        Convert a byte string to it's hex string representation e.g. for output.
        """

        # Uses list comprehension which is a fractionally faster implementation than
        # the alternative, more readable, implementation below
        #   
        #    hex = []
        #    for aChar in byteStr:
        #        hex.append( "%02X " % ord( aChar ) )
        #
        #    return ''.join( hex ).strip()        

        return ''.join(["%02X" % ord(x) for x in byte_str]).strip()

    @staticmethod
    def hex_to_byte(hex_str):
        """
        Convert a string hex byte values into a byte string. The Hex Byte values may
        or may not be space separated.
        """
        # The list comprehension implementation is fractionally slower in this case    
        #
        #    hexStr = ''.join( hexStr.split(" ") )
        #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
        #                                   for i in range(0, len( hexStr ), 2) ] )

        bytes = []

        hex_str = ''.join(hex_str.split(" "))

        for i in range(0, len(hex_str), 2):
            bytes.append(chr(int(hex_str[i:i + 2], 16)))

        return ''.join(bytes)

    @staticmethod
    def array_to_hex(byte_arr):
        """
        Convert a byte array to it's hex string representation e.g. for output.
        """

        # Uses list comprehension which is a fractionally faster implementation than
        # the alternative, more readable, implementation below
        #   
        #    hex = []
        #    for aChar in byte_arr:
        #        hex.append( "%02X " %  aChar  )
        #
        #    return ''.join( hex ).strip()        

        return ''.join(["%02X" % x for x in byte_arr]).strip()

    @staticmethod
    def hex_to_array(hex_str):
        """
        Convert a string hex byte values into a byte array. The Hex Byte values may
        or may not be space separated.
        """
        # The list comprehension implementation is fractionally slower in this case    
        #
        #    hexStr = ''.join( hexStr.split(" ") )
        #    return ''.join( ["%c" %  int ( hexStr[i:i+2],16 )  \
        #                                   for i in range(0, len( hexStr ), 2) ] )

        bytes = []

        hex_str = ''.join(hex_str.split(" "))

        for i in range(0, len(hex_str), 2):
            bytes.append(int(hex_str[i:i + 2], 16))

        return bytes

    @staticmethod
    def md5(str):
        hs = md5.new()
        hs.update(str.encode(encoding='utf-8'))
        return hs.hexdigest()

    @staticmethod
    def xor_encrypt(data, key='awesomepassword'):
        from itertools import izip, cycle
        xored = [ord(x) ^ ord(y) for (x, y) in izip(data, cycle(key))]
        return PathCrypt.array_to_hex(xored).strip()

    @staticmethod
    def xor_decrypt(data, key='awesomepassword'):
        from itertools import izip, cycle
        data = PathCrypt.hex_to_byte(data)
        xored = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in izip(data, cycle(key)))
        return xored

    @staticmethod
    def xor_path(file_path, key='awesomepassword', crypt_len=16, random_position=8):
        l = len(file_path)
        print("path leng %d" % l)
        if l > crypt_len:
            if random_position >= crypt_len:
                random_position = 1
            i = 0
            crypt = file_path[0:i + crypt_len]
            ext = []
            ext.append(crypt[random_position:random_position + 1])
            while (i + crypt_len <= l):
                i += crypt_len;
                next = file_path[i:i + crypt_len]
                if i + random_position < l:
                    ext.append(next[random_position:random_position + 1])
                print("current:%s,next:%s,ext:%s" % (crypt, next, "".join(ext)))
                crypt = PathCrypt.hex_to_byte(PathCrypt.xor_encrypt(crypt, next))
            file_path = PathCrypt.hex_to_byte(
                PathCrypt.xor_encrypt(crypt, "".join(ext)))
        file_path = PathCrypt.xor_encrypt(file_path, key)
        # first char as folder
        file_path = os.path.join(file_path[0], file_path)
        return file_path

    @staticmethod
    def md5_path(file_path, key='awesomepassword'):
        file_path = key + "_" + file_path;
        file_path = PathCrypt.md5(file_path)
        # first char as folder
        file_path = os.path.join(file_path[0], file_path)
        return file_path

    # @staticmethod
    # def xor_encrypt2(data,key):
    # ldata=len(data)
    # lkey=len(key)
    # secret=[]
    # num=0
    # for each in data:
    # if num>=lkey:
    # num=num%lkey
    # secret.append(ord(each)^ord(key[num]))
    # num+=1

    # return ''.join( [ "%02X" %  x for x in secret ] ).strip()

    # @staticmethod
    # def xor_decrypt2(secret,key):

    # data = secret.decode('hex')

    # ldata=len(data)
    # lkey=len(key)
    # secret=[]
    # num=0
    # for each in data:
    # if num>=lkey:
    # num=num%lkey

    # secret.append( chr( ord(each)^ord(key[num]) ) )
    # num+=1

    # return "".join( secret )
