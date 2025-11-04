import time
import hmac
import hashlib
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

def load_key(key_file):
    try:
        with open(key_file, 'rb') as f:
            encrypted_key = f.read()
        with open(key_file + ".enc", 'rb') as f:
            encryption_key = f.read()
        
        fernet = Fernet(encryption_key)
        decrypted_key = fernet.decrypt(encrypted_key).decode()

        return decrypted_key

    except FileNotFoundError:
        print("Error: Could not find file:", key_file)
        exit(1)
    except Exception as e:
        print("Error: Could not decyrpt key file:", e)
        exit(1)


def generate_otp(key_hex):
    key_bytes = bytes.fromhex(key_hex)

    # conver 30 second time intervals to 8 byte array 
    time_counter = int(time.time() // 30)
    time_bytes = time_counter.to_bytes(8, byteorder='big')

    hmac_result = hmac.new(key_bytes, time_bytes, hashlib.sha1).digest()

    # dynamic truncation: truncate using the last byte
    offset = hmac_result[-1] & 0x0f
    truncated = hmac_result[offset:offset+4]

    # convert to int and get last 6 digits
    code = int.from_bytes(truncated, byteorder='big') & 0x7fffffff
    otp = code % 1000000

    return (f"{otp:06d}")

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
    key = load_key(args.k)
    otp = generate_otp(key)
    print(otp)

else:
    parser.print_help()
    exit(1)





