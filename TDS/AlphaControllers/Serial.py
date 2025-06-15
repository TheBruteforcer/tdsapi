import random
import string

def generate_serial_code(length=6):
    characters = string.ascii_uppercase + string.digits
    serial_code = ''.join(random.choices(characters, k=length))
    return serial_code


