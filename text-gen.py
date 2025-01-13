import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import fitz  
from tabulate import tabulate

def parse_sitemap(sitemap_file):
    with open(sitemap_file, "r") as file:
        sitemap_content = file.read()

    root = ET.fromstring(sitemap_content)
    urls = [url.text for url in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    return urls

def convert_pdf_to_markdown(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code != 200:
        print(f"Failed to download PDF from {pdf_url}")
        return ""

    pdf_doc = fitz.open(stream=response.content, filetype="pdf")
    markdown_content = ""

    for page_num in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_num)
        markdown_content += f"## Page {page_num + 1}\n\n"
        markdown_content += page.get_text("text") + "\n\n"

    return markdown_content

def scrape_page(url):
    response = requests.get(url)
    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        print(f"Non-HTML content detected: {url}")
        return "", [], []

    soup = BeautifulSoup(response.content, "html.parser")

    text_content = "\n".join([p.get_text() for p in soup.find_all("p")])

    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
            rows.append(cells)
        if rows:
            markdown_table = tabulate(rows, headers="firstrow", tablefmt="github")
            tables.append(markdown_table)

    return text_content, tables

def extract_pdfs(url):
    response = requests.get(url)
    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        print(f"Skipping non-HTML page: {url}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    pdf_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".pdf"):
            pdf_url = href if href.startswith("http") else url + href
            pdf_links.append(pdf_url)

    return pdf_links

def write_to_file(output_file, url, text_content, tables, pdf_links):
    with open(output_file, "a") as file:
        file.write(f"URL: {url}\n\n")
        file.write("## Text Content:\n")
        file.write(text_content + "\n\n")

        if tables:
            file.write("## Tables (Markdown):\n\n")
            for table in tables:
                file.write(table + "\n\n")

        if pdf_links:
            file.write("## PDFs Converted to Markdown:\n\n")
            for pdf in pdf_links:
                file.write(f"- [PDF]({pdf})\n")
                markdown_content = convert_pdf_to_markdown(pdf)
                if markdown_content:
                    file.write(markdown_content + "\n\n")

        file.write("\n" + "=" * 80 + "\n\n")

def main():
    sitemap_file = "sitemap_cleaned.xml"
    output_file = "website_content.md"

    urls = parse_sitemap(sitemap_file)

    for url in urls:
        print(f"Scraping {url}...")
        try:
            text_content, tables = scrape_page(url)
            pdf_links = extract_pdfs(url)
            write_to_file(output_file, url, text_content, tables, pdf_links)
        except Exception as e:
            print(f"Error processing {url}: {e}")

    print(f"All content saved to {output_file}")

if __name__ == "__main__":
    main()
