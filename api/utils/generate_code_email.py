import random


def get_random_code():
    code = str(random.randint(0, 9999))
    print("0" * (4 - len(code)) + code)
    return "0" * (4 - len(code)) + code