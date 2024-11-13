from Cryptodome.Cipher import AES
from binascii import unhexlify
import zlib

key = unhexlify('a5f41376d435dc6c61ef9ddf2c4a9543c7d68ec746e690fe391bf1604362742f')
iv = unhexlify('95e61ead02c32dab646478048203fd0b')

data_offset = 0x2883a0
data_size = 0x18fb40

cipher = AES.new(key, AES.MODE_CBC, iv)

with open('MsMpEng.exe', 'rb') as f:
    encrypted_packer_data = f.read()[data_offset:data_offset + data_size]

packer_data = cipher.decrypt(encrypted_packer_data)
data = zlib.decompress(packer_data)

with open('unpack_msmpeng', 'wb') as f:
    f.write(data)
