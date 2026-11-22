import requests

REQUEST_TIMEOUT_SECONDS = 10


def count_lines(filename):
    with open(filename, encoding="utf-8") as f:
        return sum(1 for _ in f)


def count_characters(filename):
    with open(filename, encoding="utf-8") as f:
        return sum(len(line) for line in f)


def count_bytes(url):
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return len(response.content)
