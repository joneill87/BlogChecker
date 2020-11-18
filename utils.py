import re


def strip_protocol_identifier(url) -> str:
    return re.sub("http[s]?\:\/\/", "", url)


def get_domain_only(url) -> str:
    if ".com" in url:
        return url[0:url.index('.com')] + '.com'.strip('/')
    else:
        return url.strip('/')

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
