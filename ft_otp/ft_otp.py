import time
import hmac
import hashlib
import sys
import argparse
from cryptography.fernet import Fernet

def validate_key(secret_file):
    with open(secret_file, 'r') as f:
        key = f.read().strip()
    
    if len(key) != 64:
        print("Error: ket must be 64 hexadecimal characters.")
        exit(1)

    try:
        int(key, 16)
    except ValueError:
        print("Error: key must be hexadecimal")
        exit(1)
    return (key)

time_counter = int(time.time() // 30)
time_bytes = time_counter.to_bytes(8, byteorder='big')

hmac_result = hmac.new(key, time_bytes, hashlib.sha1).digest()

offset = hmac_result[-1] & 0x0f
truncated = hmac_result[offset:offset+4]

code = int.from_bytes(truncated, byteorder='big') & 0x7fffffff
otp = code % 1000000


parser = argparse.ArgumentParser()

parser.add_argument('-g', type=str, help="The program receives as argument a hexadecimal key of at least 64 characters. " \
    "The program stores this key safely in a file called ft_otp.key, which is encrypted.")
parser.add_argument('-k', type=str, help="The program generates a new temporary password based on the key given as argument" \
    "and prints it on the standard output.")


args = parser.parse_args()

if args.g:
    key = validate_key(args.g)
    save(key)

elif args.k:
    key = l