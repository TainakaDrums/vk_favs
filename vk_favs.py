import vk
import os
import time
import threading
from etaprogress.progress import ProgressBar
import sys
from itertools import count
from urllib import request
from concurrent.futures import ThreadPoolExecutor
import logging


"""
1. Open url in browser.
https://oauth.vk.com/authorize?client_id=5385901&redirect_uri=https://oauth.vk.com/blank.html&scope=offline,friends&response_type=token&v=5.62
2. Allow acsess
3. Сopy access_token value
4. Paste it to TOKEN variable
"""

TOKEN=""


def download_pics(url, dirname, bar):

    filename=url.split("/")[-1]
    path = os.path.join(dirname, filename)

    if not os.path.exists(path) :

        try:
            res=request.urlopen(url)
            if res.getcode() != 200:
                return

            pic=res.read()
            with open(path, "wb") as f:
                f.write(pic)
        except Exception as e:
            logger.error("{0}.  URL IS {1}".format(e, url))

    bar.numerator += 1
    print(bar, end='\r')
    sys.stdout.flush()


def get_urls(api):

    for number in count(0, 500):

        response=  api.fave.getPhotos(offset = number, count = 500)[1:] + api.fave.getPosts(offset = number, count = 500)[1:]

        if not len(response):
            break

        for content in response:
            if content.get("attachments"):
                for attachment in content.get("attachments"):
                    attached_pic_links=attachment.get("photo", {})
                    url = extract_url(attached_pic_links)
                    if url:
                        yield  url
            else:
                url = extract_url(content)
                if url:
                    yield  url

        time.sleep(1)


def extract_url(content) :

    for key in ("srx_xxbig", "src_xbig", "src_big", "src"):
        if content.get(key):
            return content.get(key)


def mkdir():
    dirname = os.path.join(os.environ.get("USERPROFILE", os.environ.get("HOME")), "vk_favs")
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    return dirname


def main():
    session = vk.Session(TOKEN)
    api = vk.API(session)
    dirname = mkdir()

    bar = ProgressBar(0, max_width=50)
    bar.numerator = 0

    urls = get_urls(api)

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda url: download_pics(url, dirname, bar), urls)
        
if __name__ == "__main__":

    logger = logging.getLogger()

    if not TOKEN:
        logger.error("TOKEN variable is empty")
        exit()

    main()

    print() #NEED FOR PROGRESS BAR
