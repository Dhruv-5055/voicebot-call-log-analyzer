import re

PHONE_PATTERN = re.compile(r"(\+?91[- ]?)?[6-9]\d{9}")


def is_valid_phone(number):
    return PHONE_PATTERN.fullmatch(str(number).strip()) is not None