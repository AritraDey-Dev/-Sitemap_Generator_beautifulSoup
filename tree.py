import os
import urllib.parse
import xml.etree.ElementTree as ET

xml_file = "sitemap_fixed.xml" 
tree = ET.parse(xml_file)
root = tree.getroot()

namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

output_dir = "folder_structure"
os.makedirs(output_dir, exist_ok=True)

for url in root.findall("ns:url/ns:loc", namespace):
    loc = url.text
    if loc:
        parsed_url = urllib.parse.urlparse(loc)
        path = parsed_url.path.lstrip("/")  
        full_path = os.path.join(output_dir, path)

        if "." in os.path.basename(full_path):
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(f"Placeholder for {os.path.basename(full_path)}")
        else:
            os.makedirs(full_path, exist_ok=True)

print(f"Folder structure created in: {output_dir}")
