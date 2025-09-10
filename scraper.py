import requests
from bs4 import BeautifulSoup
import os
import json
from slugify import slugify  # pip install python-slugify

RSS_URL = "https://datamacautoday.blogspot.com/feeds/posts/default?alt=rss"
OUTPUT_DIR = "images"

def scrape_images():
    response = requests.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    xml = response.text

    # pake parser lxml
    soup = BeautifulSoup(xml, "lxml-xml")
    items = soup.find_all("item")

    index_data = []

    for item in items:
        title = item.find("title").text.strip()
        folder_name = slugify(title)
        folder_path = os.path.join(OUTPUT_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

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
                img_data = requests.get(src, timeout=10).content
                filename = f"{slugify(title)}_{i}.jpg"
                filepath = os.path.join(folder_path, filename)

                with open(filepath, "wb") as f:
                    f.write(img_data)

                data.append({"filename": filename, "url": src})
            except Exception as e:
                print(f"  Failed {src}: {e}")

        # simpan json per post
        json_path = os.path.join(folder_path, "data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": title,
                "folder": folder_name,
                "count": len(data),
                "images": data
            }, f, ensure_ascii=False, indent=2)

        # tambahin ke index.json
        index_data.append({
            "title": title,
            "folder": folder_name,
            "count": len(data)
        })

    # simpan index.json
    with open(os.path.join(OUTPUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print("Scraping done.")

if __name__ == "__main__":
    scrape_images()
