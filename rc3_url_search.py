import requests
import urllib.parse
from multiprocessing.pool import ThreadPool
import re
import pickle
import time
import pathlib

ALL_DATA = []
ALL_URL = []
ERROR_COUNTER = 0
URL_COUNTER = 0
IMG_COUNTER = 0
e = []

def pprint(*args, **kwargs):
    global i
    global URL_COUNTER
    global ERROR_COUNTER
    global IMG_COUNTER
    print(f"i:{i},u:{URL_COUNTER}:{IMG_COUNTER},e:{ERROR_COUNTER}:", *args, **kwargs)


def dump(filename, data):
    global i
    global URL_COUNTER
    global ERROR_COUNTER
    with open(filename, 'wb') as f:
        pickle.dump({"iteration":i, "URL_COUNTER":URL_COUNTER, "ERROR_COUNTER":ERROR_COUNTER, "data":data}, f)


def flatten(l):
    if type(l) == tuple:
        yield l
    else:
        for i in l:
            for j in flatten(i):
                yield j


# urls = ["https://metalab.maps.at.rc3.world//map.json"]
scrape_url = ["https://lobby.maps.at.rc3.world/main.json"]
REGEX = re.compile(r'\s*"name": ?"([^"]+)",\s*"opacity": ?\w+,\s*"properties":\[\s*\{\s*"name": ?"(?:(?:exitSceneUrl)|(?:exitUrl))",\s*"type": ?"\w+",\s*"value": ?"([^"]+)"\s*\}\],\s*', re.MULTILINE)
IMG_REGEX = re.compile(r'\s*"image": ?"([^"]+)"\s*', re.MULTILINE)


def create_structure(url, content):
    host = urllib.parse.urlparse(url).hostname
    file_ = pathlib.Path("files/" + host + "/" + urllib.parse.urlparse(url).path)
    file_.parent.mkdir(parents=True, exist_ok=True)
    file_.write_bytes(content.encode())


def download_url(url):
    global ERROR_COUNTER
    global ALL_DATA
    global URL_COUNTER
    global IMG_COUNTER
    global e
    # assumes that the last segment after the / represents the file name
    # if url is abc/xyz/file.txt, the file name will be file.txt
    pprint(f"url: {url}")
    content = None
    for i in range(3):
        try:
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                content = r.content.decode()
            else:
                ERROR_COUNTER += 1
                c = r.content.decode().replace('\n', '\\n')
                pprint(f"HTTPS ERROR: {r.status_code} on {url} with {c}")
                continue
            break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
            pprint(url)
            pprint("retry")
    if not content:
        e.append(url)
        return []

    matches = REGEX.findall(content)
    matches_absolut = []
    for match in matches:
        url_un = urllib.parse.unquote(match[1]).replace("\\/", "/").replace("../", "").split("#")[0]
        #pprint(f"url_un: {url_un}")
        #pprint(url_un)
        #pprint(f"match: {match}")
        if match[1][:4] == "http":
            data_tuple = (match[0], url_un)
        else:
            data_tuple = (match[0], "https://" + urllib.parse.urlparse(url).hostname + "/" + url_un)
        if data_tuple[1] in ALL_URL:
            pass
        else:
            create_structure(url, content)
            ALL_DATA.append(data_tuple)
            ALL_URL.append(data_tuple[1])
            URL_COUNTER = len(ALL_DATA)
            matches_absolut.append(data_tuple)

    matches_img = IMG_REGEX.findall(content)

    if url[-4:] == 'json':
        base_url = '/'.join(url.split("/")[:-1])
    else:
        base_url = url
    if base_url[-1] != "/":
        base_url += "/"

    for img in matches_img:
        img_url = urllib.parse.unquote(base_url + img).replace("\\/", "/").replace("../", "")
        host = urllib.parse.urlparse(img_url).hostname
        path = urllib.parse.urlparse(img_url).path
        filepath = pathlib.Path("files/" + host + "/" + path).parent
        filepath.mkdir(parents=True, exist_ok=True)
        file = filepath.joinpath(img_url.split("/")[-1])
        if not file.exists() or False:
            pprint(f"url: {url} -> {img}")
            IMG_COUNTER += 1
            img = requests.get(img_url)
            img_file = open(file, "wb")
            img_file.write(img.content)
            img_file.close()


    return matches_absolut




i = 0
results = list(flatten(ThreadPool(15).imap_unordered(download_url, scrape_url)))
while True:
    if results != []:
        scrape_url = list(map(lambda x: x[1], results))
        results = list(flatten(ThreadPool(15).imap_unordered(download_url, scrape_url)))
    else:
        print()
        print()
        print(e)
        dump(f"{time.strftime('%Y-%m-%d_%H-%M-%S')}_finished_iter_{i}.pkl", ALL_DATA)
        break
    i += 1
r"""
"name": "([^"]+)",\s*
"opacity": \w+,\s*
"properties": \[\s*
    \{\s*
        "name": "(exitSceneUrl)|(exitUrl)",\s*
        "type": "\w+",\s*
        "value": "([^"]+)"\s*
    \}\],
"""