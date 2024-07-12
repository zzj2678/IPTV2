from urllib.parse import parse_qs, urlparse


def get_url_params(url):
    query = parse_qs(urlparse(url).query)
    return {k: v[0] if v and len(v) == 1 else v for k, v in query.items()}
