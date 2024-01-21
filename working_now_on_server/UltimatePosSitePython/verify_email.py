import re


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def check(email):
    if (re.fullmatch (regex, email)):
        print("Valid Email")
        return "Success"
    else:
        print("Invalid Email")
        return "Invalid"


