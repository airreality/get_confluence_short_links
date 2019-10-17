import json
import re
import subprocess

import lxml.html as html
import requests

from config import (CONFLUENCE_DOMAIN, CONFLUENCE_LOGIN, CONFLUENCE_PASS,
                    FILE_DST, FILE_SRC)


def is_string_url(string):
    print(string)
    pattern = re.compile(r"https://docs[a-zA-Z0-9\/\.-]+(#.*)?")

    if pattern.fullmatch(string):
        return True

    return False


def is_url_alive(url):
    command = f"curl -L -s -o /dev/null -w \"%{{http_code}}\" {url}"
    proc = subprocess.run(command, shell=True, capture_output=True)
    out = proc.stdout.decode("utf-8")
    print(out)

    if out == "200":
        return True

    return False


def get_url_anchor(url):
    anchor = url.find('#')
    if anchor != -1:
        return url[anchor:]

    return False


def get_page_id(url):
    content = requests.get(url)
    content_html = html.document_fromstring(content.text)
    page_id = content_html.xpath('//body/@pageid')
    print(page_id)

    return page_id[0]


def cf_authorize(login, passwd):
    """Сессия в Confluence"""
    try:
        s = requests.Session()
        s.auth = (login, passwd)

        return s
    except:
        print("ERROR: NOT_AUTHORIZED")
        exit()


def get_short_url(session, page_id):
    desc_url = f"https://{CONFLUENCE_DOMAIN}/rest/api/content/{page_id}"
    content = session.get(desc_url)
    jcontent = json.loads(content.text)
    short_url = jcontent['_links']['tinyui']
    domain = jcontent['_links']['base']
    result = f"{domain}{short_url}"
    print(result)

    return result


def main():
    with open(FILE_SRC, 'r') as file_src:
        with open(FILE_DST, 'a') as file_dst:
            file_dst.truncate(0)
            session = cf_authorize(CONFLUENCE_LOGIN, CONFLUENCE_PASS)

            for line in file_src:
                line = line.rstrip()

                if not is_string_url(line):
                    file_dst.write(line)
                elif not is_url_alive(line):
                    file_dst.write('')
                else:
                    page_id = get_page_id(line)
                    url_anchor = get_url_anchor(line)
                    short_url = get_short_url(session, page_id)
                    if url_anchor:
                        short_url += url_anchor
                    file_dst.write(short_url)
                file_dst.write('\n')


if __name__ == "__main__":
    main()
