import os
import re
import requests
import json
import shutil
from bs4 import BeautifulSoup
from datetime import datetime

# ---------------- Config ----------------
RSS_URL = "https://datamacautoday.blogspot.com/feeds/posts/default?alt=rss"
OUTPUT_DIR = "images"
BASE_URL = "https://raw.githubusercontent.com/Iyapetai69/CdnSyair/refs/heads/main/images"

# ---------------- Helpers ----------------
def safe_folder_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    return name.strip("-")

def download_image(url, folder, idx):
    ext = os.path.splitext(url.split("?")[0])[1]
    if not ext or len(ext) > 5:
        ext = ".jpg"
    filename = f"{folder}_{idx}{ext}"
    filepath = os.path.join(OUTPUT_DIR, folder, filename)
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filename
    except Exception as e:
        print(f"❌ Gagal download {url}: {e}")
        return None

# ---------------- Main ----------------
def scrape_images():
    # bersihkan folder biar repo ga bengkak
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("📡 Ambil RSS feed...")
    resp = requests.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")

    posts = soup.find_all("item")
    all_index = []

    for post in posts:
        title = post.title.text.strip()
        folder = safe_folder_name(title)
        content_html = post.description.text if post.description else ""

        os.makedirs(os.path.join(OUTPUT_DIR, folder), exist_ok=True)

        # cari semua gambar di content
        content_soup = BeautifulSoup(content_html, "html.parser")
        img_tags = content_soup.find_all("img")
        image_urls = [img["src"] for img in img_tags if img.has_attr("src")]

        print(f"📰 {title} -> {len(image_urls)} gambar")

        images_data = []
        for i, img_url in enumerate(image_urls, 1):
            filename = download_image(img_url, folder, i)
            if filename:
                images_data.append({
                    "filename": filename,
                    "url": f"{BASE_URL}/{folder}/{filename}"
                })

        # save data.json per folder
        data_path = os.path.join(OUTPUT_DIR, folder, "data.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": title,
                "folder": folder,
                "count": len(images_data),
                "images": images_data
            }, f, ensure_ascii=False, indent=2)

        # append ke index.json
        if images_data:
            all_index.append({
                "title": title,
                "folder": folder,
                "count": len(images_data),
                "cover_url": images_data[0]["url"]
            })

    # simpan index.json global
    with open(os.path.join(OUTPUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(all_index, f, ensure_ascii=False, indent=2)

    print("✅ Selesai scrape & simpan data")

if __name__ == "__main__":
    scrape_images()
