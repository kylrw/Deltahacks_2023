import os
import openai
import json
import AccessKeys
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import jsonify


app = Flask(__name__) #create new rest api

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

import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession

def get_claims(article):
    """
    Given article returns json containing main claims of the article and google search queries to further research these claims.
    """

    article = """
    On Monday, extremely credible and incredibly accurate reports revealed that Joe Biden will be attending the first presidential debate Tuesday night with an earpiece hidden in his auditory canal and methamphetamine screaming through his blood.

    These revelations — which definitely are not baseless conspiracies fomented by the Trump campaign in a last-ditch effort to prepare its supporters for the vast disparity between what they’ve been told Joe Biden is like (a man suffering from late-stage dementia) and what he is actually like (an old man who sometimes misspeaks but remains competent at retail politics) — helped spur a new round of reporting on the Democratic nominee’s debate preparations Tuesday afternoon.

    First, journalist Todd Starnes of The Starnes Media Group (no relation), reported that the Iowa radio station KXEL had itself reported that the “word on the street” was that Joe Biden “got tonight’s debate questions in advance.”

    Word on the street is that @JoeBiden got tonight's debate questions in advance - per @KXEL1540

    — toddstarnes (@toddstarnes) September 29, 2020
    As of this writing, it is not clear which street in Eastern Iowa KXEL heard this word on. But in the journalism business, few have more credibility than Todd Starnes, who worked his way up from the ground-floor of Starnes Media Group — overcoming unfounded suspicions of nepotism at every turn — to become the company’s first-ever president with the surname Starnes, making him an inspiration to Starneses the world-over, few of whom ever thought they’d live to see the day that Starnes Media Group was led by a natural-born Starnes.

    Sign up for Dinner Party
    A lively evening newsletter about everything that just happened.

    Enter your email
    Now, Intelligencer has learned that Biden will not only enter tonight’s debate with the benefit of an earpiece and advance knowledge of Chris Wallace’s questions — but also, with a next generation version of Amazon’s Alexa neurally implanted in his cerebral cortex. A source who wished to remain anonymous said that, according to a Biden family member’s college roommate’s golfing buddy’s Facebook post, the super-intelligent microchip can feed perfect answers directly into the Democratic nominee’s consciousness. Thus, the source explained, should Biden fall short of complete oratorical perfection at any point in Tuesday night’s proceedings, viewers should interpret this as proof that the Democratic nominee is essentially brain-dead, his cognitive faculties too fried to so much as faithfully echo the immaculate zingers of his in-built AI. Tellingly, Biden has refused to consent to a pre-debate brain scan to prove that there is no tiny homunculus lodged behind his eyes.

    Meanwhile, a separate insider told Intelligencer that a Kamala Harris confidante’s son’s stalker’s Pinterest comment revealed Tuesday that Biden had his larynx removed late last week, and replaced with a perfect clone of Morgan Freeman’s — an operation that will cause the former vice president’s voice to sound at least three times as sonorous tonight as it is in reality. The insider further said that, according to a 4chan poster with knowledge of the situation, the Biden campaign abducted actor Cillian Murphy on Monday morning and gouged out his eyes, so as to replace their candidate’s dull peepers with the Irish thespian’s bright blue gems. Finally, according to Benny Johnson of Turning Point USA, in a last-minute procedure at Walter Reed Medical Center this afternoon, Biden had both of his arms sawed off and replaced with M20B1 “Super Bazookas.”
    """

    promt = f"""
    Extract a list of 8 most controversial claims made by the following article, for use in a fake news detector's claim verification pipeline. Export the claims in the specified JSON schema. The claims should strictly be only in factoid form, paraphrased to be minimal and easy to understand. Alongside the claims, export a search query that can be used to look on the internet for evidence supporting or contradicting the claim. The search query should be rephrased to have no polarity towards being for or against the claim.
    
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
    for i in claim_list:
        results = google_search(i["search_query"])
        print("------------------------------------------ NEW PROMPT ------------------------------------------")
        for i in results:
            #call to scrape for html
            print(i["link"])


def send_email(text):
	subject = "FakeBlock Report"  # create a string that is the subject
	emailText = 'Subject: {}\n\n{}'.format(subject, text)  # set the subject of emailText to the subjec above

	sender, password = 'grahamTestMaker@gmail.com', 'TestMakePassword1'  # t #the sender username then password MUST GMAIL ACCOUNT, dont hack me pls :)
	recieve = "graham.morrison2003@gmail.com"  # define the reciever...
	message = emailText  # the message
	port = 465  # standard ssl port - router could block ssl port

	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:  # access the gmail server
		server.login(sender, password)  # login to gmail account
		server.sendmail(sender, recieve, message)  # send mail

@app.route("/fakeblock", methods=["POST"])
def main():
    info = request.json #request the json
    url = info["url"]
    openai.api_key = os.getenv("OPENAI_API_KEY")
    #article = scrape_contents()
    article = ""
    claim_list = get_claims(article)
    google_claims(claim_list)
    
    send_email("Test")
    return jsonify({'message':'Success!'})

if __name__ == '__main__':
    app.run()