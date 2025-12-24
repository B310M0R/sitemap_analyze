import requests
from xml.etree import ElementTree
import sys

sensitive_keywords = [
    "admin", "login", "config", "backup", "secret", "private",
    "user", "credential", "password", "key", "token", "internal",
    "hidden", "debug", "test", "staging", "dev", "api", "db", "database"
]

def parse_sitemap(xml_content):
    urls = []
    try:
        tree = ElementTree.fromstring(xml_content)
        # Находим все loc
        for elem in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(elem.text)
    except ElementTree.ParseError as e:
        print(f"Error parsing sitemap XML: {e}")
    return urls

def find_sensitive_urls(urls):
    sensitive_urls = []
    for url in urls:
        if any(keyword.lower() in url.lower() for keyword in sensitive_keywords):
            sensitive_urls.append(url)
    return sensitive_urls

def fetch_sitemap(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"Error fetching sitemap {url}: {e}")
        return None

def process_sitemap(url, collected_urls):
    xml_content = fetch_sitemap(url)
    if not xml_content:
        return

    urls = parse_sitemap(xml_content)
    for u in urls:
        # Проверяем, является ли URL ссылкой на другой sitemap
        if u.endswith(".xml") and u not in collected_urls:
            process_sitemap(u, collected_urls)
        else:
            collected_urls.add(u)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_sitemap.py <full_sitemap_url>")
        sys.exit(1)

    sitemap_url = sys.argv[1]
    all_urls = set()

    process_sitemap(sitemap_url, all_urls)

    all_urls = sorted(all_urls)
    print(f"Total URLs found: {len(all_urls)}\n")

    print("All URLs found:")
    for u in all_urls:
        print(u)

    sensitive = find_sensitive_urls(all_urls)
    print(f"\nSensitive URLs found ({len(sensitive)}):")
    for u in sensitive:
        print(u)
