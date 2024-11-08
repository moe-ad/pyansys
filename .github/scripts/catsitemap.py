import re
import xml.etree.ElementTree as ET
import requests
from xml.dom import minidom

def extract_urls_and_headers(url: str) -> tuple:
    """This function extracts projects names and sitemap.xml urls for each project

    Args:
        url (str): link to the .rst file of the PyAnsys documentation landing page

    Returns:
        tuple: returns a tuple of list of project names and list of urls to projects' sitemap.xml files
    """
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        print("Timed out while trying to get request")
        raise

    content = response.text

    # Extract section headers and URLs (modify regex based on your needs)
    project_names = [project_name.strip() for project_name in re.findall(r'\.\. grid-item-card:: ([\w\s-]+)', content)]
    urls = re.findall(r':link: (https://[\w./-]+)', content)

    # Modify URLs
    updated_urls = [re.match(r"^(https:\/\/[^\/]+)", url).group(1) + "/sitemap.xml" for url in urls]

    # Filter none existent URLS
    valid_project_names = []
    valid_urls = []
    for index, url in enumerate(updated_urls):
        if requests.get(url).status_code == 404:
            continue
        else:
            valid_project_names.append(project_names[index])
            valid_urls.append(url)

    return valid_project_names, valid_urls

def generate_sitemap_index(url: str) -> None:
    """This function generates a sitemap_index.xml file indexing other sitemap.xml files

    Args:
        url (str): link to the .rst file of the PyAnsys documentation landing page
    """

    # Create the root element with namespace
    sitemap_index = ET.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Build the list of urls
    urls = extract_urls_and_headers(url)[1]

    # Create sitemap elements for each URL
    for url in urls:
        sitemap = ET.SubElement(sitemap_index, "sitemap")
        loc = ET.SubElement(sitemap, "loc")
        loc.text = url

    # Format XML with indentation
    rough_string = ET.tostring(sitemap_index, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")    

    # Create the tree and write to XML file
    with open("globalsitemap.xml", "w") as f:
        f.write(pretty_xml)


# URL of the .rst
URL = "https://docs.pyansys.com/version/dev/_sources/index.rst.txt"
generate_sitemap_index(URL)