# import requests
# from bs4 import BeautifulSoup
# import json

# BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
# TDS_CATEGORY = "/c/tools-for-data-science-jan-2025/68"

# def get_posts(start_page=0, end_page=10):
#     posts = []
#     for i in range(start_page, end_page):
#         url = f"{BASE_URL}{TDS_CATEGORY}?page={i}"
#         print(f"Scraping: {url}")
#         resp = requests.get(url)
#         soup = BeautifulSoup(resp.text, 'html.parser')
#         for link in soup.select("a.title.raw-link"):
#             post_url = BASE_URL + link['href']
#             post_text = link.text
#             posts.append({"url": post_url, "text": post_text})
#     return posts

# with open("tds_discourse_posts.json", "w") as f:
#     json.dump(get_posts(), f, indent=2)

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import time

# URL to the TDS Jan 2025 category - update if needed
CATEGORY_URL = "https://discourse.onlinedegree.iitm.ac.in/c/tds/jan2025.json"
TOPIC_BASE_URL = "https://discourse.onlinedegree.iitm.ac.in/t/"

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 4, 14)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": "_forum_session=0u%2BHLqCq%2BeoIUTWYx1GDcB1Vonvnxk%2FgOmC6%2Bt5nIqzi4uz7HCupZNw0WbFzJaDwx21nKPwuxcxC9BvW6x%2FYG80q6Bra6ERX5G%2BWllkT%2BT6Io%2FXxFPO%2BYmVjR6VrloNi3JMmfttcN5D4Ze9f%2FHEBBDG8Ux6aRkSQ5QCNuGIAla1jEhBV8cN4OQ9ch%2Fa17CvrrW6f2Ajuvg7O0EokVPBRLn8F5lO7p%2B3%2FwkjmRbl6L49V%2BlXQ7OvBTzzZCbQsqnBD6o2t82W9ccFysuw2RW4xpkysp8NGgu209Tc4rEH%2B9DIHCIWKNBxqEQImUTdjX0IqBBamxbmstdYH6zVZlvNED8Sw72K9CxH%2F0hpmsMR26ESrd7MoiWWJyC37Dm29YcGRV%2BtA9cFCK4AIAmOJYIhGIMRmx4JoGEzniOycwr1HX3a0EJGpasOFvp%2BO0VVWFJdztx95Boaa7sRxDsf4QvXj2Tb4x4Mc8lmoHGNafO1mdF8qLnKKga3rR2HQ6t7dMv4CS9E%3D--m%2BMizTLt0wgY1cM7--HVWzVd%2BBRINnsmaz5vfsVw%3D%3D"
}

def get_all_topics():
    print("[+] Fetching topics...")
    topics = []
    page = 0
    while True:
        url = f"{CATEGORY_URL}?page={page}"
        print(f"[i] Fetching: {url}")
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print("[!] Failed to fetch page:", response.status_code)
            break
        data = response.json()
        topic_list = data.get("topic_list", {}).get("topics", [])
        if not topic_list:
            break
        topics.extend(topic_list)
        page += 1
        time.sleep(0.5)  # be nice to the server
    print(f"[+] Found {len(topics)} topics.")
    return topics

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text().strip()

def get_posts_from_topics(topics):
    print("[+] Collecting posts within date range...")
    posts_data = []
    for topic in topics:
        topic_id = topic["id"]
        slug = topic["slug"]
        url = f"{TOPIC_BASE_URL}{slug}/{topic_id}.json"
        print(f"[i] Fetching topic: {url}")
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"[!] Skipping topic {topic_id} due to error {response.status_code}")
                continue
            topic_data = response.json()
            for post in topic_data["post_stream"]["posts"]:
                created_at = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
                if START_DATE <= created_at.date() <= END_DATE:
                    posts_data.append({
                        "topic_id": topic_id,
                        "topic_slug": slug,
                        "created_at": created_at.isoformat(),
                        "username": post["username"],
                        "content": clean_html(post["cooked"]),
                        "post_number": post["post_number"],
                        "post_url": f"{TOPIC_BASE_URL}{slug}/{topic_id}/{post['post_number']}"
                    })
        except Exception as e:
            print(f"[!] Exception for topic {topic_id}: {e}")
        time.sleep(0.5)
    print(f"[+] Collected {len(posts_data)} posts.")
    return posts_data

def save_posts(posts, filename="tds_discourse_filtered.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved posts to {filename}")

if __name__ == "__main__":
    topics = get_all_topics()
    posts = get_posts_from_topics(topics)
    save_posts(posts)
