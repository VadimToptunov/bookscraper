import time
from bs4 import BeautifulSoup


def save_to_file(filename, text):
    txt_filename = f"{filename}.html"
    with open(txt_filename, "a") as bk:
        bk.write("<pre>" + text + "</pre> <br>\n")


def parse_page(url, session):
    resp = session.get(url)
    return BeautifulSoup(resp.text, "html.parser")


def get_last_page(soup_object):
    last_page = soup_object.find("div", {"id": "div_paginator"})
    return last_page.find_all("a")[-1].text


def get_book_text(url, session):
    try:
        soup = parse_page(url, session)
    except Exception as ex:
        print(ex)
        sleep()
        soup = parse_page(url, session)
    return soup.find("div", {"id": "ptext"}).text


def sleep():
    time.sleep(180)
    print("Have to sleep")


def get_text(book_text_url_tmp, filename, session):
    book_text = get_book_text(book_text_url_tmp, session)
    save_to_file(filename.replace("[", "").replace("]", ""), book_text)
