import xml.etree.ElementTree as ET

# File names
input_file = "sitemap_fixed.xml"
output_file = "sitemap_cleaned.xml"
log_file = "cleanup_log.txt"

def remove_redundant_links(input_file, output_file, log_file):
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()

        namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        ET.register_namespace('', namespace)
        seen_urls = set()
        removed_urls = []
        
        for url_element in root.findall(f".//{{{namespace}}}url"):
            loc_element = url_element.find(f"{{{namespace}}}loc")
            if loc_element is not None:
                url = loc_element.text.strip()
                if url.lower() in seen_urls:
                    root.remove(url_element)
                    removed_urls.append(url)
                else:
                    seen_urls.add(url.lower())

        tree.write(output_file, encoding="UTF-8", xml_declaration=True)

        with open(log_file, "w") as log:
            log.write("Sitemap Cleanup Log\n")
            log.write(f"Input file: {input_file}\n")
            log.write(f"Output file: {output_file}\n")
            log.write("Removed URLs:\n")
            for url in removed_urls:
                log.write(f"- {url}\n")
            log.write(f"Total removed: {len(removed_urls)}\n")

        print("Cleanup completed successfully. Check the log file for details.")

    except ET.ParseError as e:
        print(f"Error parsing {input_file}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
remove_redundant_links(input_file, output_file, log_file)
