import requests
from bs4 import BeautifulSoup

def scrape_discourse():
    base_url = "https://discourse.onlinedegree.iitm.ac.in"
    category_url = base_url + "/c/courses/tds-kb/34"

    try:
        res = requests.get(category_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/t/") and "tds" in href and href not in links:
                links.append(href)

        # Convert to absolute URLs
        absolute_links = [base_url + link for link in links[:5]]
        return absolute_links

    except Exception as e:
        return [f"Error fetching discourse: {str(e)}"]
