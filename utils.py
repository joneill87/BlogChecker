import re
import os
import sys


def get_makeo_template_path() -> str:
    return f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/ReportTemplate.mako"


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
