import re

MFT_PATH = 'C:/Users/Forensics/Desktop/htb/safecracker/WinServer-Collection/uploads/ntfs/%5C%5C.%5CC%3A/$MFT'

with open(MFT_PATH, 'rb') as f:
    mft_data = f.read()

filenames = list()

ransom_extension = '.31337'.encode('utf-16-le')

# search for utf-16 string that ends with the ransom extension
for match in re.finditer(ransom_extension, mft_data):
    # get its index in the mft
    filename_end = match.end()
    # reverse search the next null byte (the start of the string)
    filename_start = mft_data[:filename_end].rfind(b'\x00\x00')
    # copy the match into the list of all filenames
    # skip first 4 bytes
    # 2 bytes = \x00\x00
    # 2 bytes = garbage (?) file ID in mft?
    filenames.append(mft_data[filename_start+0x4:filename_end].decode('utf-16-le'))

# filter unique filenames
filenames = set(filenames)

for filename in filenames:
    print(filename)

print(f'Found {len(filenames)} unique encrypted filenames')
