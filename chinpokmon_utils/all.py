from pprint import pprint
import bs4
import requests
from selenium import webdriver
from contextlib import contextmanager
import numpy as np
import cv2
import time


def mypprint(*args, **kwargs):
    for i in args:
        pprint(i, **kwargs)


def BS(url):
    return bs4.BeautifulSoup(requests.get(url).content, features="lxml")


def content2cvimage(content):
    nparr = np.frombuffer(content, np.uint8)
    # error if nparr.size == 0
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def get_onload(driver, by, element, timeout=3):
    while not len(driver.find_elements(by, element)) > 0:
        time.sleep(1)
        if timeout > 0:
            timeout -= 1
        else:
            raise TimeoutError
    return driver.find_element(by, element)


@contextmanager
def connect(visible=True, mute=True):
    try:
        chrome_options = webdriver.chrome.options.Options()
        if mute:
            chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--start-maximized")
        if visible == False:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--log-level=3")

        driver = webdriver.Chrome(
            options=chrome_options)
        yield driver
    except Exception as e:
        print("Connection closed, due an error")
        print(e)
    finally:
        try:
            driver.quit()
        except:
            pass


def create_session(driver=None, visible=False):
    if driver == None:
        with connect(visible) as driver:
            cookies = driver.get_cookies()
    else:
        cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie["name"], cookie["value"])
    return session
