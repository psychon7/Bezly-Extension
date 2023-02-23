import json
import os
import requests
from bs4 import BeautifulSoup
import tiktoken
import re
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

HEADERS = ({
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    })

# productName = "Logitech-920-007596-Multi-Device-Bluetooth-Keyboard"
# productASIN = "B0148NPH9I"
# productWebsite = "amazon.in"

openai.api_key = "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"

app = Flask(__name__)
CORS(app)
# Firebase configuration
config = {
  "apiKey": "AIzaSyCc-8m1CpnWO6-sNuAUJbHz-k_QtwdDgX4",
  "authDomain": "bezly-26df5.firebaseapp.com",
  "projectId": "bezly-26df5",
  "storageBucket": "bezly-26df5.appspot.com",
  "messagingSenderId": "18422235356",
  "appId": "1:18422235356:web:def787e4cf59251da1f419",
  "measurementId": "G-PQD5N5MC85"

}

# user define function
# Scrape the data
def getdata(url):
    r = requests.get(url, headers=HEADERS)
    return r.text
  
def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_ai_response(prompt):
  response = openai.Completion.create(
    model="davinci:ft-personal:amznreviewsummary-2023-02-17-17-09-20",
    prompt=prompt+" ###",
    temperature=0.7,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=["END"]
  )

  text = response.choices[0].text

  pc = text.split('\n\n')
  print(pc)

#   pc = {'Pros': ['Compact and portable\nSeamless switching between devices\nComfortable typing experience\nEasy setup:'], 'Cons': ["Smaller size may take some getting used to for those with larger hands\nDoesn't have a backlight\nOverall, the Logitech K380 is a great choice for anyone who wants a versatile, portable keyboard that's easy to setup and use across multiple devices. The typing experience is comfortable and the connectivity is excellent. "]}

  for i, element in enumerate(pc):
    if '\nCons:' in element:
        pc[i] = element.replace('\nCons:', '')
        pc.insert(i+1, 'Cons:')
        break
    
  if '' in pc:  
    pc.remove('')

  print(pc)
  try:
    one_line_summary = pc[0].split(": ")[1]
    pros = pc[pc.index("Pros:") + 1: pc.index("Cons:")]
    cons = pc[pc.index("Cons:") + 1:]

    if '\n' in pros:
        pros_list = pc['Pros'][0].split('\n')
        pros = pros_list

    if '\n' in cons:
        cons_list = pc['Cons'][0].split('\n')
        cons = cons_list

    result = {"One_Line": one_line_summary, "Pros": pros, "Cons": cons}

    print(json.dumps(result, indent=4))
    return json.dumps(result, indent=4)
  except:
    # result = {"Pros": pros, "Cons": cons}
    print("Err")
  
def html_code(url):
  
    # pass the url
    # into getdata function
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')
  
    # display html code
    return (soup)

def cus_rev(soup):
    # find the Html tag
    # with find()
    # and convert into string
    data_str = ""
  
    for item in soup.find_all("span", class_="a-size-base review-text review-text-content"):
        data_str = data_str + item.get_text()
  
    result = data_str.split("\n")
    return (result)
 
def mainFunction(pw, pn, pa):
    url = "https://"+pw+"/"+pn+"/product-reviews/"+pa+"/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
    soup = html_code(url)
    rs = cus_rev(soup)
    strs = ""
    for r in rs:
        strs = strs + r.replace("\n", "")

    tokes = num_tokens_from_string(strs, "gpt2")
    print(tokes)

    tokens = re.findall(r'\S+', strs)[:1600]
    final_text = " ".join(tokens)
    print(final_text)

    res = get_ai_response(final_text)

if __name__ == '__main__':
    app.run()
