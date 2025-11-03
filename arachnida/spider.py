from sys import argv
import argparse
import requests as rq

parser = argparse.ArgumentParser()

parser.add_argument('url')
parser.add_argument('-r', '--recursive', action='store_true')
parser.add_argument('-l', '--depth', type=int, default=5)
parser.add_argument('-p', '--path', type=str, default='./data/')

args = parser.parse_args()

url = args.url
recursive = args.recursive
max_depth = args.depth
path = args.path

if max_depth and not recursive:
    print("Error: -l requires -r flag")
    exit(1)

if max_depth > 0:
    print("Error: -l requires a valid number")
    exit(1)

visited_urls = set()

def spider(url, current_depth):
    if url in visited_urls or current_depth > max_depth:
        return
    visited_urls.add(url)