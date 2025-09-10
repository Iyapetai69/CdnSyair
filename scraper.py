import os
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

# Ambil HTML dari target
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

# Cari semua gambar di dalam div.separator
images = []
for div in soup.find_all("div", class_="separator"):
    img = div.find("img")
    if img and img.get("src"):
        images.append(img.get("src"))

# Simpan gambar ke folder
saved_files = []
for i, src in enumerate(images, start=1):
    if src.startswith("//"):
        src = "https:" + src
    elif src.startswith("/"):
        src = URL.rstrip("/") + src

    try:
        img_data = requests.get(src).content
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
