import os
import shutil
import xxtea
import utils


class FileCrypt:

    def __init__(self, key, sign):
        self.key = key
        self.sign = sign

    def encrypt_dir(self, src_dir, out_dir, include=None):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for filename in os.listdir(src_dir):
            file_path = os.path.join(src_dir, filename)
            out_path = os.path.join(out_dir, filename)

            if os.path.isdir(file_path):
                self.encrypt_dir(file_path, out_path, include)
            elif os.path.isfile(file_path):
                if utils.in_rules(file_path, include):
                    FileCrypt.encrypt(file_path, out_path, self.key, self.sign)
                else:
                    shutil.copy(file_path, out_path)

    def decrypt_dir(self, src_dir, out_dir, include=None):
        for filename in os.listdir(src_dir):
            file_path = os.path.join(src_dir, filename)
            out_path = os.path.join(out_dir, filename)
            if os.path.isdir(file_path):
                self.decrypt_dir(file_path, out_path, include)
            elif os.path.isfile(file_path):
                if utils.in_rules(file_path, include):
                    FileCrypt.decrypt(file_path, out_path, self.key, self.sign)
                else:
                    shutil.copy(file_path, out_path)

    @staticmethod
    def encrypt(file_path, out_path, key, sign):
        print("===>encrypt %s to %s" % (file_path, out_path))
        fp = open(file_path, "rb")
        encrypt_bytes = xxtea.encrypt(fp.read(), key)
        fp.close()

        encrypt_bytes = sign + encrypt_bytes

        # out_dir = os.path.dirname(out_path)
        # if not os.path.exists(out_dir):
        #     os.makedirs(out_dir)
        fp = open(out_path, "wb")
        fp.write(encrypt_bytes)
        fp.close()

    @staticmethod
    def decrypt(file_path, out_path, key, sign):
        print("===>decrypt %s to %s" % (file_path, out_path))
        fp = open(file_path, "rb")
        encrypt_bytes = fp.read()
        fp.close()

        sign_len = len(sign)
        if encrypt_bytes[:sign_len] == sign:
            decrypt_bytes = xxtea.decrypt(encrypt_bytes[sign_len:], key)
            out_dir = os.path.dirname(out_path)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            fp = open(out_path, "wb")
            fp.write(decrypt_bytes)
            fp.close()

    def start_encrypt(self, src_path, out_path, include=None, remove_source=True):
        if src_path == out_path:
            bak_path = src_path + "_bak"
            if os.path.exists(bak_path):
                shutil.rmtree(bak_path)
            os.rename(src_path, bak_path)
            self.encrypt_dir(bak_path, out_path, include)
            if remove_source:
                shutil.rmtree(bak_path)
        else:
            self.encrypt_dir(src_path, out_path, include)
            if remove_source:
                shutil.rmtree(src_path)
