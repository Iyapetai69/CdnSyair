import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
from urllib.parse import urlparse
import re

URL = "https://datamacautoday.blogspot.com/2025/04/syair-macau.html?m=1"

def scrape_images():
    # ambil HTML
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    html = response.text

    # save debug
    with open("response.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved response.html for debugging")

    # parse HTML
    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")

    print(f"Found {len(img_tags)} images")

    # bikin folder images
    os.makedirs("images", exist_ok=True)

    # nama file pakai tanggal
    today = datetime.utcnow().strftime("%Y%m%d")
    data = []
    counter = 1

    for img in img_tags:
        src = img.get("src") or img.get("data-src") or img.get("data-original")
        if not src:
            continue

        # cek ekstensi
        parsed = urlparse(src)
        ext_match = re.search(r"\.(jpg|jpeg|png|gif)", parsed.path, re.IGNORECASE)
        ext = ext_match.group(0) if ext_match else ".jpg"

        filename = f"PrediksiMacau{today}_{counter}{ext}"
        filepath = os.path.join("images", filename)

        try:
            img_data = requests.get(src, timeout=10).content
            with open(filepath, "wb") as f:
                f.write(img_data)
            data.append({"filename": filename, "url": src})
            print(f"Saved {filename}")
            counter += 1
        except Exception as e:
            print(f"Failed to download {src}: {e}")

    # save json
    with open("images/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Scraping done.")

if __name__ == "__main__":
    scrape_images()
