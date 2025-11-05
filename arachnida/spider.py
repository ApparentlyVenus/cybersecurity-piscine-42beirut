from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import argparse
import requests as rq

parser = argparse.ArgumentParser()

parser.add_argument("url")
parser.add_argument("-r", "--recursive", action="store_true", help="activate recursive mode")
parser.add_argument("-l", "--depth", type=int, help="max depth for recursive calls")
parser.add_argument("-p", "--path", type=str, default="./data/", help="set download path")

args = parser.parse_args()

url = args.url
recursive = args.recursive
max_depth = args.depth
path = args.path

if max_depth and not recursive:
    print("Error: -l requires -r flag")
    exit(1)

visited_urls = set()

if recursive and not max_depth:
    max_depth = 5

if not recursive:
    max_depth = 0

if max_depth < 0:
    print("Error: -l requires a valid number")
    exit(1)

try:
    base_domain = urlparse(url).netloc

except ValueError:
    print("Error: Invalid start URL:", url)
    exit(1)


def downloadImgs(url, imgs):
    for img in imgs:
        img_url = img.get("src")
        if not img_url:
            continue
        try:
            absolute_url = urljoin(url, img_url)
            img_response = rq.get(absolute_url)
            img_data = img_response.content
            
            # returns just the path without any other parameters / directories
            img_parsed = urlparse(absolute_url)
            filename = os.path.basename(img_parsed.path)

            if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
                continue
            
            # here checking if img already exists
            base, extension = os.path.splitext(filename)

            filepath = os.path.join(path, filename)
            counter = 1

            while os.path.exists(filepath):
                new_filename = base + "(" + str(counter) + ")" + extension
                filepath = os.path.join(path, new_filename)
                counter += 1

            if counter > 1:
                filename = os.path.basename(filepath)

            with open(filepath, "wb") as f:
                f.write(img_data)
            
            print("Downloaded:", filename)

        except Exception as e:
            print("Failed to download", img_url, ":", e)
            continue

def spider(url, current_depth):
    if url in visited_urls or (recursive and current_depth > max_depth):
        return
    visited_urls.add(url)

    try:
        print("Scrapping url:", url, "At depth", current_depth)
        response = rq.get(url, timeout=5)
        response.raise_for_status()
        html = response.text

    except rq.exceptions.RequestException as e:
        print("Failed to retreive:", url, ":", e)
        return


    soup = BeautifulSoup(html, "html.parser")
    os.makedirs(path, exist_ok=True)
    imgs = soup.find_all("img")
    
    downloadImgs(url, imgs)
            
    links = soup.find_all("a")
    for link in links:
        href = link.get("href")

        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        try:
            absolute_url = urljoin(url, href)
            parsed_url = urlparse(absolute_url)

        except Exception as e:
            print("Skipping malformed URL:", href)
            continue

        if (parsed_url.scheme in ["http", "https"] and
            parsed_url.netloc == base_domain and
            absolute_url not in visited_urls and recursive):

            spider(absolute_url, current_depth + 1)

try:
    print("Starting spider at", url)
    print("Saving to:", path)

    if (recursive):
        print("Recursive depth:", max_depth)

    spider(url, 0)
    print("Spider finished!")

except rq.exceptions.RequestException as e:
    print("Error: Could not reach for", url, ":", e)
    exit(1)

except KeyboardInterrupt:
    print("\nSpider stopped by user")
    exit(0)
