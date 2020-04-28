#!/usr/bin/env python3.8

import json
import re

import lxml.html as html
import requests

from config import (CONFLUENCE_DOMAIN, CONFLUENCE_LOGIN, CONFLUENCE_PASS,
                    FILE_DST, FILE_SRC)


def is_string_url(string):
    return bool(re.compile(r"https://[a-zA-Z0-9\/\.-\?]+(#[a-zA-Z0-9\/\.-\?]+)?").fullmatch(string))


def is_url_alive(url):
    return requests.get(url).status_code == 200


def get_url_anchor(url):
    return url[anchor:] if (anchor := url.find('#')) != -1 else ''


def get_page_id(url):
    return html.document_fromstring(
        requests.get(url).text
    ).xpath('//body/@pageid')[0]


def get_confluence_session(login, passwd):
    session = requests.Session()
    session.auth = (login, passwd)

    return session


def get_short_url(session, page_id):
    content = session.get(f"{CONFLUENCE_DOMAIN}/rest/api/content/{page_id}").json()

    return f"{content['_links']['base']}{content['_links']['tinyui']}"


def main():
    with open(FILE_SRC, 'r') as file_src:
        with open(FILE_DST, 'a') as file_dst:
            file_dst.truncate(0)
            session = get_confluence_session(CONFLUENCE_LOGIN, CONFLUENCE_PASS)

            for line in file_src:
                line = line.rstrip()

                if not is_string_url(line):
                    print(line)
                    file_dst.write(line)
                elif not is_url_alive(line):
                    print('')
                    file_dst.write('')
                else:
                    page_id = get_page_id(line)
                    short_url = get_short_url(session, page_id)

                    if url_anchor := get_url_anchor(line):
                        short_url += url_anchor
                    print(short_url)
                    file_dst.write(short_url)
                file_dst.write('\n')


if __name__ == "__main__":
    main()
