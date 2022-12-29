import os

import requests
import pypandoc
from bs4 import BeautifulSoup

categories = [2, 3, 4, 5, 6, 8, 43, 54, 74, 75, 91]
basic_url = "http://book-online.com.ua/index.php?cat="
blocker = "Доступ к книге заблокирован по требованию правообладателя!"


def request_categories():
    for i in categories:
        url = f"{basic_url}{i}"
        bs = parse_page(url)
        last_link = get_last_page(bs)
        paginate(last_link, url)


def paginate(last_link, url):
    last_link_range = int(last_link) + 1
    for i in range(1, last_link_range):
        soup = parse_page(f"{url}&page={i}")
        blocks = soup.find_all("div", {"class": "block1"})
        for block in blocks:
            book_data = block.find_all("a")
            get_books(book_data)


def save_to_file(filename, text):
    txt_filename = f"{filename}.html"
    with open(txt_filename, "a") as bk:
        bk.write("<pre>" + text + "</pre> <br>\n")


def parse_page(url):
    resp = requests.get(url)
    bs = BeautifulSoup(resp.text, "html.parser")
    return bs


def get_last_page(soup_object):
    last_page = soup_object.find("div", {"id": "div_paginator"})
    return last_page.find_all("a")[-1].text


def get_book_text(url):
    soup = parse_page(url)
    return soup.find("div", {"id": "ptext"}).text


def get_books(book_data):
    book = book_data[3]["href"]
    book_text = get_book_text(book)
    book_name = book_data[0].text
    author = book_data[1].text
    category = book_data[2].text
    filename = f"{category}__{author}-{book_name}"
    if blocker not in book_text:
        soup = parse_page(book)
        last_book_page = int(get_last_page(soup)) + 1
        for i in range(1, last_book_page):
            book_text = get_book_text(f"{book}&page={i}")
            save_to_file(filename, book_text)
            print(f"{filename}: page: {i}/{last_book_page}")
        pypandoc.convert_file(f"{filename}.html", 'epub', outputfile=f"{filename}.epub")
        os.remove(f"{filename}.html")

    else:
        print(f"{filename} - Ignored")
        pass


if __name__ == '__main__':
    request_categories()
