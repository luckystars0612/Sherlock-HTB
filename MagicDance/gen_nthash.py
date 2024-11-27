import hashlib

password = "P@ssw0rd1"  # Replace with the cracked password
nt_hash = hashlib.new('md4', password.encode('utf-16le')).hexdigest()
print(f"NT Hash: {nt_hash}")
