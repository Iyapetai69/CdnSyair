import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# URL target scrape
URL = "https://datamacautoday.blogspot.com/2025/04/syair-macau.html?m=1"

# Folder simpan gambar
OUTPUT_DIR = "images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ambil tanggal hari ini
today = datetime.now().strftime("%Y%m%d")

# Ambil HTML dengan header User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}
response = requests.get(URL, headers=headers)
html = response.text
soup = BeautifulSoup(html, "html.parser")

# Cari semua div.separator
images = []
for div in soup.find_all("div", class_="separator"):
    div_html = str(div)

    # Regex cari semua <img ...>
    matches = re.findall(r'<img[^>]+>', div_html, re.IGNORECASE)

    for tag in matches:
        # Cari src / data-original / data-src
        src_match = re.search(r'(src|data-original|data-src)="([^"]+)"', tag)
        if src_match:
            src = src_match.group(2)
            if src.startswith("//"):
                src = "https:" + src
            images.append(src)

print(f"Found {len(images)} images")

# Simpan gambar ke folder
saved_files = []
for i, src in enumerate(images, start=1):
    try:
        img_data = requests.get(src, headers=headers).content
        filename = f"PrediksiMacau{today}_{i}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(img_data)
        saved_files.append(filepath)
        print(f"Saved: {filepath}")
    except Exception as e:
        print(f"Failed to download {src}: {e}")

# Buat data.json
json_data = {
    "date": today,
    "count": len(saved_files),
    "images": saved_files
}

json_path = os.path.join(OUTPUT_DIR, "data.json")
with open(json_path, "w", encoding="utf-8") as jf:
    json.dump(json_data, jf, indent=2)

print(f"Saved JSON: {json_path}")
