import re


def match1(text, *patterns):
    for pattern in patterns:
        try:
            match = re.search(pattern, text)
        except (TypeError):
            match = re.search(pattern, str(text))
        if match:
            return match.group(1)
    return None


def matchall(text, patterns):
    ret = []
    for pattern in patterns:
        try:
            match = re.findall(pattern, text)
        except (TypeError):
            match = re.findall(pattern, str(text))
        ret += match
    return ret