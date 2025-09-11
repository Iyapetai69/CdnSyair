import requests
from bs4 import BeautifulSoup
import os
import json
import shutil
from slugify import slugify
from PIL import Image
from io import BytesIO
from datetime import datetime

# ===== CONFIG =====
RSS_URL = "https://datamacautoday.blogspot.com/feeds/posts/default?alt=rss"
OUTPUT_DIR = "images"
BASE_URL = "https://cdn.jsdelivr.net/gh/Iyapetai69/CdnSyair@main/images"  # pake CDN
# ==================

def download_and_convert(src, save_path):
    """Download gambar, convert ke WebP, dan simpan"""
    resp = requests.get(src, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content))

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    save_path = os.path.splitext(save_path)[0] + ".webp"
    img.save(save_path, "webp", quality=85)
    return save_path

def scrape_images():
    # Hapus folder lama biar bersih
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Ambil feed RSS
    response = requests.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    xml = response.text

    soup = BeautifulSoup(xml, "lxml-xml")
    items = soup.find_all("item")

    index_data = []

    for item in items:
        title = item.find("title").text.strip()
        folder_name = slugify(title)
        folder_path = os.path.join(OUTPUT_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Ambil semua gambar di deskripsi
        desc = item.find("description")
        images = []
        if desc:
            desc_html = BeautifulSoup(desc.text, "html.parser")
            for img in desc_html.find_all("img"):
                src = img.get("src")
                if src:
                    images.append(src)

        print(f"[{title}] Found {len(images)} images")

        data = []
        for i, src in enumerate(images, start=1):
            try:
                # Nama file pakai title + tanggal jam sekarang
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d_%H%M")
                filename = f"{slugify(title)}_{timestamp}.webp"
                filepath = os.path.join(folder_path, filename)

                saved_path = download_and_convert(src, filepath)

                data.append({
                    "filename": os.path.basename(saved_path),
                    "url": f"{BASE_URL}/{folder_name}/{os.path.basename(saved_path)}"
                })
            except Exception as e:
                print(f"  Failed {src}: {e}")

        # Simpan JSON per post
        json_path = os.path.join(folder_path, "data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": title,
                "folder": folder_name,
                "count": len(data),
                "images": data
            }, f, ensure_ascii=False, indent=2)

        # Tambah ke index.json
        index_data.append({
            "title": title,
            "folder": folder_name,
            "count": len(data),
            "cover_url": data[0]["url"] if data else None
        })

    # Simpan index.json
    with open(os.path.join(OUTPUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print("Scraping done.")

if __name__ == "__main__":
    scrape_images()
