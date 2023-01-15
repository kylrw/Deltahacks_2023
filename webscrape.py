import requests
from bs4 import BeautifulSoup

def extract_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the article content
    article_content = soup.find("div", {"class": "c-entry-content"})
    if article_content is None:
        article_content = soup.find("div", {"class": "gnt_ar_b"})
    if article_content is None:
        article_content = soup.find("div", {"class": "article-content"})
    if article_content is None:
        article_content = soup.find("div", {"class": "entry-content"})
    if article_content is None:
        article_content = soup.find("div", {"class": "article-text"})
    if article_content is None:
        article_content = soup.find("div", {"class": "post-content"})
    if article_content is None:
        article_content = soup.find("div", {"class": "content"})
    if article_content is None:
        article_content = soup.find("div", {"class": "entry"})
    if article_content is None:
        article_content = soup.find("div", {"class": "article"})
    if article_content is None:
        article_content = soup.find("div", {"class": "main-content"})
    if article_content is None:
        print("Can't find the article content, please check the class name")
        return None
    # Print the article content
    return article_content.text

