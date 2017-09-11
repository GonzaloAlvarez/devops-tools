import base64
import json
from hashlib import md5, sha256, sha1
from Crypto.Cipher import AES
from Crypto import Random

class AESPCrypt(object):
    """AES PyCrypto implementation for AES 256 bits with openssl compatibility
       and chunk file read.
       Decode with command:
          $ openssl aes-256-cbc -md sha1/md5 -d -in inputfile -out outputfile
    """
    def __init__(self, password):
        self.password = password
        self.bs = AES.block_size

    def derive_key_and_iv(self, password, salt, key_length, iv_length):
        d = d_i = ''
        while len(d) < key_length + iv_length:
            d_i = sha1(d_i + password + salt).digest()
            d += d_i
        return d[:key_length], d[key_length:key_length+iv_length]

    def encrypt_file(self, inputfile, outputfile, key_length=32):
        salt = Random.new().read(self.bs - len('Salted__'))
        key, iv = self.derive_key_and_iv(self.password, salt, key_length, self.bs)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        finished = False
        with open(inputfile, 'rb') as in_file, open(outputfile, 'wb') as out_file:
            out_file.write('Salted__' + salt)
            while not finished:
                chunk = in_file.read(1024 * self.bs)
                if len(chunk) == 0 or len(chunk) % self.bs != 0:
                    padding_length = (self.bs - len(chunk) % self.bs) or self.bs
                    chunk += padding_length * chr(padding_length)
                    finished = True
                out_file.write(cipher.encrypt(chunk))
            out_file.close()
            in_file.close()

    def decrypt_file(self, inputfile, outputfile, key_length=32):
        with open(inputfile, 'rb') as in_file, open(outputfile, 'wb') as out_file:
            salt = in_file.read(self.bs)[len('Salted__'):]
            key, iv = self.derive_key_and_iv(self.password, salt, key_length, self.bs)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            next_chunk = ''
            finished = False
            while not finished:
                chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * self.bs))
                if len(next_chunk) == 0:
                    padding_length = ord(chunk[-1])
                    chunk = chunk[:-padding_length]
                    finished = True
                out_file.write(chunk)
            out_file.close()
            in_file.close()

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
    
    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, input_string):
        key = sha256(self.password.encode()).digest()
        raw = self._pad(input_string)
        iv = Random.new().read(self.bs)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, input_string):
        enc = base64.b64decode(input_string)
        iv = enc[:AES.block_size]
        key = sha256(self.password.encode()).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)

        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def encrypt_dict(self, data, whitelisted = []):
        ret_data = {}
        for key, value in data.iteritems():
            if key in whitelisted:
                ret_data[key] = value
            else:
                ret_data[key] = self.encrypt(json.dumps(value))
        return ret_data

    def decrypt_dict(self, data, whitelisted = []):
        ret_data = {}
        for key, value in data.iteritems():
            if key in whitelisted:
                ret_data[key] = value
            else:
                ret_data[key] = json.loads(self.decrypt(value))
        return ret_data

