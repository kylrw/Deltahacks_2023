import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core import BaseService, DetailedResponse
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features, CategoriesOptions

authenticator = IAMAuthenticator('R7pPaFgv5YJxfO385rQTApoYuE-DytSeDyadl29kUECy')
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator
)

natural_language_understanding.set_service_url('https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/93d343a5-3db7-4846-ad31-17a8bfb5c94a')

response = natural_language_understanding.analyze(
    url='https://nymag.com/intelligencer/2020/09/trump-biden-debate-earpiece-drugs-satire.html',
    features=Features(categories=CategoriesOptions(limit=3))).get_result()



print(response)
