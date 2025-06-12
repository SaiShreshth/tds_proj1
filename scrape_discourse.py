import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
TDS_CATEGORY = "/c/tools-for-data-science-jan-2025/68"

def get_posts(start_page=0, end_page=10):
    posts = []
    for i in range(start_page, end_page):
        url = f"{BASE_URL}{TDS_CATEGORY}?page={i}"
        print(f"Scraping: {url}")
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for link in soup.select("a.title.raw-link"):
            post_url = BASE_URL + link['href']
            post_text = link.text
            posts.append({"url": post_url, "text": post_text})
    return posts

with open("tds_discourse_posts.json", "w") as f:
    json.dump(get_posts(), f, indent=2)