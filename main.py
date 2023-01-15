import os
import openai
import AccessKeys
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

openai.api_key = os.getenv("OPENAI_API_KEY")

article = """
"""

promt = """
Extract a list of claims made by the following article, for use in a fake news detector's claim verification pipeline. Export the claims in the specified JSON schema. The claims should strictly be only in factoid form, paraphrased to be minimal and easy to understand. Alongside the claims, export a search query that can be used to look on the internet for evidence supporting or contradicting the claim. The search query should be rephrased to have no polarity towards being for or against the claim.
 
```schema
{{
    "brief_summary": string,
    "claims": [
        {{
            "claim": string,
            "search_query": string,
        }},
    ]
}}
```
 
```article
{article}
```
 
```claims
"""

#Call OpenAI API
response = openai.Completion.create(
model="text-davinci-002",
prompt=promt,
temperature=0,
max_tokens=400,
top_p=1,
frequency_penalty=0,
presence_penalty=0
)

#Parse to get data
print(response["choices"][0]["text"])
#----------------------------------------------------------------------