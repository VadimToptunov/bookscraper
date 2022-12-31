import asyncio
import os
import random
import time
from types import NoneType

import requests
import pypandoc
from bs4 import BeautifulSoup
from requests import ReadTimeout

# categories = [2, 4, 5, 6, 8, 43, 54, 74, 75, 91]
categories = [75, 91, 2]
basic_url = "http://book-online.com.ua/index.php?cat="
blocker = "Доступ к книге заблокирован по требованию правообладателя!"
book_text_url = ""
filename_tmp = ""
last_book_page_tmp = ""
pagenum = 0


async def request_categories():
    session = requests.Session()
    for i in categories:
        url = f"{basic_url}{i}"
        try:
            bs = parse_page(url, session)
        except ReadTimeout:
            __sleep()
            print("Have to sleep")
            bs = parse_page(url, session)
        try:
            time.sleep(2)
            last_link = get_last_page(bs)
            paginate(last_link, url, session)
        except Exception:
            pass


def paginate(last_link, url, session):
    last_link_range = int(last_link) + 1
    for i in range(1, last_link_range):
        try:
            soup = parse_page(f"{url}&page={i}", session)
        except ReadTimeout:
            __sleep()
            soup = parse_page(f"{url}&page={i}", session)
        blocks = soup.find_all("div", {"class": "block1"})
        for block in blocks:
            book_data = block.find_all("a")
            get_books(book_data, session)


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
    except Exception:
        __sleep()
        soup = parse_page(url, session)
    return soup.find("div", {"id": "ptext"}).text


def get_books(book_data, session):
    book = book_data[3]["href"]
    book_text = get_book_text(book, session)
    book_name = book_data[0].text
    author = book_data[1].text
    category = book_data[2].text
    filename = f"{category}__{author}-{book_name}".replace("[", "").replace("]", "")
    if blocker not in book_text:
        try:
            soup = parse_page(book, session)
        except ReadTimeout:
            soup = parse_page(book, session)
        last_book_page = int(get_last_page(soup)) + 1
        for i in range(1, last_book_page):
            book_text_url_temp = f"{book}&page={i}"
            try:
                __get_text(book_text_url_temp, filename, last_book_page, i, session)
            except KeyboardInterrupt:
                book_text_url = book_text_url_temp
                filename_tmp = filename
                last_book_page_tmp = last_book_page
                pagenum = i
        pypandoc.convert_file(f"{filename}.html", 'epub', outputfile=f"{filename}.epub")
        try:
            os.remove(f"{filename}.html")
        except Exception:
            pass

    else:
        print(f"{filename} - Ignored")
        pass


def __sleep():
    time.sleep(180)
    print("Have to sleep")


def __get_text(book_text_url_tmp, filename, last_book_page, pagenum, session):
    book_text = get_book_text(book_text_url_tmp, session)
    save_to_file(filename.replace("[", "").replace("]", ""), book_text)
    print(f"{filename}: page: {pagenum}/{last_book_page}")


if __name__ == '__main__':
    if book_text_url != "":
        session = requests.Session()
        __get_text(book_text_url, filename_tmp, last_book_page_tmp, pagenum, session)
        asyncio.get_event_loop().run_until_complete(request_categories())
    else:
        asyncio.get_event_loop().run_until_complete(request_categories())
