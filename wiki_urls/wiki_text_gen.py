import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import re
from tabulate import tabulate
import pdfplumber
import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and a stream handler
file_handler = logging.FileHandler('scrape.log')
stream_handler = logging.StreamHandler()

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def parse_sitemap(sitemap_file):
    try:
        with open(sitemap_file, "r", encoding="utf-8") as file:
            sitemap_content = file.read()

        root = ET.fromstring(sitemap_content)
        urls = [url.text for url in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        logger.info(f"Parsed sitemap file: {sitemap_file}")
        return urls
    except Exception as e:
        logger.error(f"Error parsing sitemap file: {e}")
        return []

def extract_table_from_text(text):
    rows = [row.strip() for row in text.split("\n") if row.strip()]
    table_data = [re.split(r'\s{2,}', row) for row in rows]

    column_counts = [len(row) for row in table_data]
    most_common_count = max(set(column_counts), key=column_counts.count) if column_counts else 0
    table_data = [row for row in table_data if len(row) == most_common_count]

    if len(table_data) < 2:
        logger.info("No valid tables found in text.")
        return None

    logger.info("Extracted table from text.")
    return tabulate(table_data, headers="firstrow", tablefmt="github")

def convert_pdf_to_markdown(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()

        pdf_path = "temp.pdf"
        with open(pdf_path, "wb") as file:
            file.write(response.content)

        tables_markdown = extract_table_from_pdf(pdf_path)
        pdf_doc = fitz.open(pdf_path)
        markdown_content = ""

        for page_num in range(pdf_doc.page_count):
            page = pdf_doc.load_page(page_num)
            text = page.get_text("text")
            markdown_content += f"## Page {page_num + 1}\n\n"

            if tables_markdown:
                for i, table in enumerate(tables_markdown, start=1):
                    markdown_content += f"### Table {i}\n{table}\n\n"

            markdown_content += text + "\n\n"

        logger.info(f"Converted PDF to Markdown: {pdf_url}")
        return markdown_content
    except Exception as e:
        logger.error(f"Error processing PDF from {pdf_url}: {e}")
        return ""

def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

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

        logger.info(f"Scraped URL: {url}")
        return text_content, tables
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {e}")
        return "", []

def extract_pdfs(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        pdf_links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.endswith(".pdf"):
                pdf_url = href if href.startswith("http") else requests.compat.urljoin(url, href)
                pdf_links.append(pdf_url)

        logger.info(f"Extracted PDFs from URL: {url}")
        return pdf_links
    except Exception as e:
        logger.error(f"Error extracting PDFs from {url}: {e}")
        return []

def extract_table_from_pdf(pdf_path):
    try:
        tables_markdown = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        markdown_table = tabulate(table, headers="firstrow", tablefmt="github")
                        tables_markdown.append(markdown_table)
        logger.info(f"Extracted tables from PDF: {pdf_path}")
        return tables_markdown
    except Exception as e:
        logger.error(f"Error extracting tables from PDF {pdf_path}: {e}")
        return []

def save_to_file(content, file_name="final_output.txt"):
    try:
        with open(file_name, "a", encoding="utf-8") as file:
            file.write(content + "\n\n")
        logger.info(f"Content saved to {file_name}")
    except Exception as e:
        logger.error(f"Error saving to file {file_name}: {e}")

def main(sitemap_file):
    logger.info("Starting scraping process...")

    urls = parse_sitemap(sitemap_file)
    if not urls:
        logger.error("No URLs found in sitemap. Exiting...")
        return

    logger.info(f"Found {len(urls)} URLs in the sitemap.")

    for url in urls:
        logger.info(f"Scraping URL: {url}")

        text_content, tables = scrape_page(url)

        if text_content:
            save_to_file(f"# Content from {url}\n\n{text_content}")

        if tables:
            for i, table in enumerate(tables, start=1):
                save_to_file(f"# Table {i} from {url}\n\n{table}")

        pdf_links = extract_pdfs(url)
        if pdf_links:
            logger.info(f"Found {len(pdf_links)} PDFs on {url}. Processing...")

            for pdf_url in pdf_links:
                logger.info(f"Processing PDF: {pdf_url}")
                markdown_content = convert_pdf_to_markdown(pdf_url)
                if markdown_content:
                    save_to_file(f"# Content from PDF: {pdf_url}\n\n{markdown_content}")
                else:
                    logger.warning(f"Failed to extract Markdown from PDF: {pdf_url}")

    logger.info("Scraping process completed.")

if __name__ == "__main__":
    sitemap_file = "sitemap_cleaned.xml"
    main(sitemap_file)
