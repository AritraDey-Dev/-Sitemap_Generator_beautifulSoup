import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

def crawl_website(base_url, max_depth=2):
    visited = set()
    sitemap = set()

    def crawl(url, depth):
        if depth > max_depth or url in visited:
            return
        visited.add(url)

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)

            if parsed.netloc == urlparse(base_url).netloc:
                sitemap.add(full_url)
                crawl(full_url, depth + 1)

    crawl(base_url, 0)
    return sitemap


def save_sitemap_to_file(sitemap, file_name='sitemap.xml'):
    with open(file_name, 'w') as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in sorted(sitemap):
            file.write(f'  <url>\n    <loc>{url}</loc>\n  </url>\n')
        file.write('</urlset>\n')


if __name__ == "__main__":
    urls_file = "urls.txt"
    output_directory = "sitemaps"

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Read URLs from the file
    try:
        with open(urls_file, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{urls_file}' not found.")
        exit(1)

    for idx, website_url in enumerate(urls, 1):
        print(f"Crawling website {idx}/{len(urls)}: {website_url}")
        sitemap = crawl_website(website_url)

        sitemap_file_name = os.path.join(output_directory, f'sitemap_{idx}.xml')
        print(f"Found {len(sitemap)} URLs. Saving to {sitemap_file_name}...")
        save_sitemap_to_file(sitemap, sitemap_file_name)

    print(f"All sitemaps are saved in the '{output_directory}' directory.")
