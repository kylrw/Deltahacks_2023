import os
import openai
import AccessKeys

#openai.organization = "org-UyKsO5lj2gVRNP6YefxZPkTs"
openai.api_key = os.getenv("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")

#prompt = input("Enter your promt: ")

promt = """
Extract a list of claims made by the following article, for use in a claim verification pipeline. Export the claims. Export the claims in the specified JSON schema.

'''Schema
[
    {
        "claim": string
    }
]

'''article


'''Claims:

"""

#code-davinci-002 - free because in beta
#text - costs money
response = openai.Completion.create(
model="text-davinci-002",
prompt=promt,
temperature=0,
max_tokens=400,
top_p=1,
frequency_penalty=0,
presence_penalty=0
)

print(response["choices"][0]["text"])