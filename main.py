import os
import openai
import json
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
        article_content = soup.find("div", {"class": "css-1ygdjhk evys1bk0"})
    if article_content is None:
        article_content = soup.find("div", {"class": "story-content"})
    if article_content is None:
        print("Can't find the article content, please check the class name")
        return None
    # Print the article content
    return article_content.text

import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession

def get_claims(article):
    """
    Given article returns json containing main claims of the article and google search queries to further research these claims.
    """

    promt = f"""
    Extract a list of controversial claims made by the following article (8 claims maximum), for use in a fake news detector's claim verification pipeline. Export the claims in the specified JSON schema. The claims should strictly be only in factoid form, paraphrased to be minimal and easy to understand. Alongside the claims, export a search query that can be used to look on the internet for evidence supporting or contradicting the claim. The search query should be rephrased to have no polarity towards being for or against the claim.
    
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
    max_tokens=800,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    #Parse to get data
    #print(response["choices"][0]["text"])
    response_string = response["choices"][0]["text"]

    response_string = response_string[:-3] #Cut off last 3 
    response_dict = json.loads(response_string)
    claim_dict = response_dict["claims"]

    return claim_dict

#----------------------------------------------------------------------
#Google
def get_source(url):
    """Return the source code for the provided URL. 

    Returns:
        HTTP response object from requests_html. 
    """

    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def scrape_google(query):
    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)

    links = list(response.html.absolute_links)
    google_domains = ('https://www.google.', 
                      'https://google.', 
                      'https://webcache.googleusercontent.', 
                      'http://webcache.googleusercontent.', 
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.')

    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)

    return links

def get_results(query):
    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)
    
    return response

def parse_results(response):
    css_identifier_result = ".tF2Cxc"
    css_identifier_title = "h3"
    css_identifier_link = ".yuRUbf a"
    
    results = response.html.find(css_identifier_result)
    output = []
    
    for result in results:
        item = {
            'title': result.find(css_identifier_title, first=True).text,
            'link': result.find(css_identifier_link, first=True).attrs['href'],
        }
        
        output.append(item) 
    return output

def google_search(query):
    response = get_results(query)
    return parse_results(response)


def google_claims(claim_list):

    search_results = []

    for i in claim_list:
        search_results.append("-" + i["search_query"])
        results = google_search(i["search_query"])
        for i in results:
            #call to scrape for html
            search_results.append(i["link"])
    
    return search_results

def controversial_claims(initial_article, url):

    article = extract_article(url)
    
    for i in range(2):
    
        promt = f"""
        
        Do these two articles contradict each other:
        Respond "Yes." or "No.":

        Article 1:
        {initial_article}
        Article 2:
        {article}

        """
        
        #Call OpenAI API
        response = openai.Completion.create(
        model="text-davinci-002",
        prompt=promt,
        temperature=0,
        max_tokens=800,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        #Parse to get data
        response_string = response["choices"][0]["text"]

        print(response_string)

        if response_string == "Yes.":
            return(url)
        else:
            return None

def false_claims(claim):

    for i in range(2):
    
        promt = f"""
        
        Tell me the percentage that this claim is false,
        only give the numerical value:

        {claim['claim']}

        """
        
        #Call OpenAI API
        response = openai.Completion.create(
        model="text-davinci-002",
        prompt=promt,
        temperature=0,
        max_tokens=800,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        #Parse to get data
        response_string = response["choices"][0]["text"]

        return(response_string)

if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    url = "https://nymag.com/intelligencer/2020/09/trump-biden-debate-earpiece-drugs-satire.html"
    article = extract_article(url)
    claim_list = get_claims(article)
    claim_results = google_claims(claim_list)
    controversies = []

    for claim in claim_list:
        percentage = false_claims(claim)
        percentage.replace(" ","")
        if len(percentage) <= 5:
            if int(percentage) >= 50:
                controversies.append([claim["claim"],percentage])

    #for i in claim_results:
     #   if i[0] != "-":
      #      #print(article2)
       #     controversies.append(controversial_claims(article,i))
    
    string = "We have found the following controversies:"

    for i in controversies:
        string += i[0]
        string += " Has a "
        string += i[1]
        string += "% chance that its false \n"
    
    print(string)


            
    

