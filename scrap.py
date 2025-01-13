import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

def parse_sitemap(sitemap_file):
    """Parse the sitemap file to extract URLs."""
    with open(sitemap_file, "r") as file:
        sitemap_content = file.read()

    root = ET.fromstring(sitemap_content)
    urls = [url.text for url in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    return urls

def scrape_page(url):
    """Scrape plain text and tables from the given URL."""
    response = requests.get(url)
    
    # Check Content-Type to verify if the content is HTML
    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        print(f"Non-HTML content detected: {url}")
        return "", [], []

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract plain text content
    text_content = "\n".join([p.get_text() for p in soup.find_all("p")])

    # Extract tables and convert to Markdown
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
            rows.append("| " + " | ".join(cells) + " |")
        if rows:
            header = rows[0]
            separator = "| " + " | ".join(["---"] * len(header.split("|")[1:-1])) + " |"
            rows.insert(1, separator)
            tables.append("\n".join(rows))

    return text_content, tables, None

def extract_pdfs(url):
    """Extract PDF links from the given URL."""
    response = requests.get(url)
    
    # Check Content-Type to verify if the content is HTML
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
    """Write all content to a single text file in a structured format."""
    with open(output_file, "a") as file:
        file.write(f"URL: {url}\n\n")  # Add URL for reference
        file.write("## Text Content:\n")
        file.write(text_content + "\n\n")

        if tables:
            file.write("## Tables (Markdown):\n\n")
            for table in tables:
                file.write(table + "\n\n")

        if pdf_links:
            file.write("## PDFs:\n\n")
            for pdf in pdf_links:
                file.write(f"- [PDF]({pdf})\n")

        file.write("\n" + "=" * 80 + "\n\n")  # Separator for clarity

def main():
    """Main script to parse sitemap, scrape content, and write to a file."""
    sitemap_file = "sitemap_cleaned.xml"  # Path to your sitemap file
    output_file = "website_content.txt"  # Output file

    # Parse sitemap
    urls = parse_sitemap(sitemap_file)

    for url in urls:
        print(f"Scraping {url}...")
        try:
            text_content, tables, _ = scrape_page(url)
            pdf_links = extract_pdfs(url)
            write_to_file(output_file, url, text_content, tables, pdf_links)
        except Exception as e:
            print(f"Error processing {url}: {e}")

    print(f"All content saved to {output_file}")

if __name__ == "__main__":
    main()
