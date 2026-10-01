import datetime
import os
import shutil
import tempfile
import time
import zipfile
from contextlib import contextmanager
from pprint import pprint

import bs4
import cv2
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Timer:
    def __init__(self):
        self.start_time = time.time()

    @property
    def elapsed(self):
        return time.time() - self.start_time


class timed_loop:
    def __init__(self, *args, **kwds):
        self._run_time = datetime.timedelta(*args, **kwds).total_seconds()
        self.i = -1
        self.timer = Timer()

    def __iter__(self):
        return self

    def __next__(self):
        self.i += 1
        if self.timer.elapsed < self._run_time:
            return self.i, self.timer
        raise StopIteration


def mypprint(*args, **kwargs):
    for i in args:
        pprint(i, **kwargs)


def BS(url):
    return bs4.BeautifulSoup(requests.get(url).text, features="lxml")


def content2cvimage(content):
    nparr = np.frombuffer(content, np.uint8)
    # error if nparr.size == 0
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def get_onload(driver, by, element: str, timeout: float=3):
    while not len(driver.find_elements(by, element)) > 0:
        time.sleep(1)
        if timeout > 0:
            timeout -= 1
        else:
            raise TimeoutError
    return driver.find_element(by, element)


@contextmanager
def connect(visible=True, mute=True):
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--log-level=3")
    if mute:
        chrome_options.add_argument("--mute-audio")
    if visible == False:
        chrome_options.add_argument("--headless")

    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_experimental_option(
    #     'excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    try:
        yield driver
    except Exception as e:  # noqa: BLE001
        print("Connection closed, due an error")
        print(e)
    finally:
        driver.quit()



def create_session(driver=None, visible=False):
    if driver == None:
        with connect(visible) as d:
            cookies = d.get_cookies()
    else:
        cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie["name"], cookie["value"])
    return session


@contextmanager
def sleep(seconds):
    start_time = time.time()
    yield
    estimated_time = time.time() - start_time
    if estimated_time < seconds:
        time.sleep(seconds - estimated_time)


def norm_filename(filename, banned_symbols='|/\\*?:<>"', placeholder="_"):
    for i in banned_symbols:
        filename = filename.replace(i, placeholder)
    return filename

# platforms: linux-arm64, linux64, mac-arm64, mac-x64, win32, win64
def update_chromedriver(platform="win64", chromedriver_dir="dependencies"):
    chromedriver_dir = os.path.realpath(chromedriver_dir)
    os.makedirs(chromedriver_dir, exist_ok=True)
    version_filepath = os.path.join(
        chromedriver_dir, "chromedriver_version.txt")
    if os.path.exists(version_filepath) and os.path.isfile(version_filepath):
        with open(version_filepath, "r") as f:
            chromedriver_version = f.read()
    else:
        with open(version_filepath, "w") as f:
            chromedriver_version = None
    resp = requests.get("https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE") # version_url
    if resp.ok:
        latest_version = resp.text
        if chromedriver_version != latest_version:
            download_base_url = "https://storage.googleapis.com/chrome-for-testing-public"
            filename = "chromedriver-" + platform + ".zip"
            resp = requests.get(f"{download_base_url}/{latest_version}/{platform}/{filename}") # download_url
            if resp.ok:
                with tempfile.TemporaryDirectory() as temp:
                    zip_path = os.path.join(temp, filename)
                    with open(zip_path, "wb") as f:
                        f.write(resp.content)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extract(f"chromedriver-{platform}/chromedriver.exe", path=temp)
                    shutil.move(os.path.join(temp, f"chromedriver-{platform}/chromedriver.exe"), os.path.join(chromedriver_dir, "chromedriver.exe"))
                    with open(version_filepath, "w") as f:
                        f.write(latest_version)
    os.environ["PATH"] += ";" + chromedriver_dir
