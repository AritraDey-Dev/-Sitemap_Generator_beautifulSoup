import re


with open("sitemap.xml", "r") as file:
    content = file.read()

fixed_content = re.sub(r'&(?!amp;)', '&amp;', content)

with open("sitemap_fixed.xml", "w") as file:
    file.write(fixed_content)

print("Fixed sitemap saved as sitemap_fixed.xml")
