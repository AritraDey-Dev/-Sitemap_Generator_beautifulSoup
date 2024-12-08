# Sitemap Fixer and Folder Structure Generator

This project helps you generate a sitemap (`sitemap.xml`), fix common issues in the XML file, and create a readable folder structure from it. Follow the steps below to set up and use the project.

---

## **Setup**

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip package manager
- xmllint (`sudo apt install libxml2-utils`)

### Installation
Install the required Python packages:
```bash
pip install requests bs4 urllib3
```

---

## **Usage**

### 1. Generate the `sitemap.xml`
Run the `main.py` script to generate the `sitemap.xml` file in your directory:
```bash
python3 main.py
```

This script will fetch the necessary data and create a `sitemap.xml` file in your project directory.

---

### 2. Validate the XML File
Use `xmllint` to validate the generated `sitemap.xml`:
```bash
xmllint sitemap.xml --noout
```

If there are issues with the XML file, the command will display the errors.

---

### 3. Fix the XML File
Run the `fix_sitemap.py` script to fix the errors in the `sitemap.xml`:
```bash
python3 fix_sitemap.py
```

This script will process the `sitemap.xml` and attempt to fix common errors. 

---

### 4. Revalidate the XML File
Run `xmllint` again to check for any remaining issues:
```bash
xmllint sitemap.xml --noout
```

If no errors are shown, you can proceed to the next step.

---

### 5. Generate the Folder Structure
Run the `tree.py` script to create a folder structure based on the fixed `sitemap.xml`:
```bash
python3 tree.py
```

This will generate a folder structure in your project directory.

---

### 6. Get a Pretty Output of the Tree
To get a readable and pretty output of the folder structure, use the `tree.sh` script:
1. Make the script executable:
   ```bash
   chmod +x tree.sh
   ```
2. Run the script:
   ```bash
   ./tree.sh
   ```

This will append the tree output to a file named `folder_structure.txt`.

---

## **Scripts Overview**
- **`main.py`**: Generates the `sitemap.xml`.
- **`fix_sitemap.py`**: Fixes issues in the `sitemap.xml`.
- **`tree.py`**: Reads the fixed `sitemap.xml` and generates a folder structure.
- **`tree.sh`**: Appends a pretty version of the folder structure to `folder_structure.txt`.

---

