import random
import string


def generate_random_string(length):
    alphanumeric_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(alphanumeric_chars) for _ in range(length))


ref_id = generate_random_string(6)
print(ref_id)