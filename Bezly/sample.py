import re
from bs4 import BeautifulSoup
from flask import Flask, request
import openai
import requests
import json
from flask_cors import CORS
import jwt
import firebase_admin
from firebase_admin import db
import time

from functions import getdata, num_tokens_from_string

openai.api_key = "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"

app = Flask(__name__)
CORS(app)

cred = firebase_admin.credentials.Certificate('./config/service.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://bezly-26df5-default-rtdb.asia-southeast1.firebasedatabase.app'
})

root_ref = db.reference()

# REST API routes
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data['email']
    password = data['password']

    url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyCc-8m1CpnWO6-sNuAUJbHz-k_QtwdDgX4"
    headers = {'Content-Type': 'application/json'}
    data = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.ok:
        uid=response.json()['localId']
        try:
            RegisternewUser(uid)
        except:
            raise ValueError(response.json()['error']['message'])
        
        return response.json()
    else:
        raise ValueError(response.json()['error']['message'])
    
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data['email']
    password = data['password']

    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCc-8m1CpnWO6-sNuAUJbHz-k_QtwdDgX4"
    headers = {'Content-Type': 'application/json'}
    datas = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }
    response = requests.post(url, headers=headers, data=json.dumps(datas))
    if response.ok:
        return response.json()
    else:
        print(ValueError(response.json()['error']['message']))

@app.route('/verifyToken', methods=['POST'])
def verify_firebase_token():
    data = request.get_json()
    token = data['token']
    decoded_token = jwt.decode(token)
    print(decoded_token)
    
    try:
        decoded_token = jwt.decode(token, verify=False)
        print(decoded_token)
        exp = decoded_token['exp']
        current_time = int(time.time())
        print(exp)
        return exp > current_time
    except:
        return False
    
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

def getASINNumner(url):
    data = getdata(url)
    print(data)
    soup = BeautifulSoup(data, 'html.parser')

    asin = soup.find('input', {"id": "ASIN"})['value']
    return asin
    
def get_ai_response(prompt, uid):
  response = openai.Completion.create(
    model="davinci:ft-personal:amznreviewsummary-2023-02-17-17-09-20",
    prompt="The prompt is a corpus of text of amazon  reviews about a product.  Generate a summary of the review in the below format One line summary: Pros: Cons:"+prompt+" ###",
    temperature=0.3,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=["END"]
  )

  text = response.choices[0].text

  pc = text.split('\n\n')
  print(pc)

#   pc = {"One_Line": "The Logitech K380 is a compact and portable wireless keyboard that's easy to take with you on the go and works seamlessly across multiple devices.","Pros": ["Compact and portable\nSeamless switching between devices\nComfortable typing experience\nEasy setup"],"Cons": ["Smaller size may take some getting used to for those with larger hands\nDoesn't have a backlight"]
# }

  for i, element in enumerate(pc):
    if '\nCons:' in element:
        pc[i] = element.replace('\nCons:', '')
        pc.insert(i+1, 'Cons:')
        break

  for i, element in enumerate(pc):
    if '\nPros:' in element:
        pc[i] = element.replace('\Pros:', '')
        pc.insert(i+1, 'Pros:')
        break
    
  if '' in pc:  
    pc.remove('')

  try:
    if ": " in pc[0]:
        one_line_summary = pc[0].split(": ")[1]
    
    if ":" in pc[0]:
        one_line_summary = pc[0].split(":")[1]

    if pc[0] == " One line summary:" or pc[0] == "One line summary:":
        one_line_summary = pc[1]
    
    for i in range(len(pc)):
        if pc[i].startswith("Pros"):
            pc[i] = "Pros:"

    for i in range(len(pc)):
        if pc[i].startswith("Cons"):
            pc[i] = "Cons:"

    pros = pc[pc.index("Pros:") + 1: pc.index("Cons:")]
    cons = pc[pc.index("Cons:") + 1:]
    print(pros, cons)

    if '\n' in pros:
        pros_list = pc['Pros:'][0].split('\n')
        print(pros_list)
        pros = pros_list

    if '\n' in cons:
        cons_list = cons[0].split('\n')
        print(cons_list)
        cons = cons_list

    if 'One line summary:' in cons:
        cons_index = cons.index("One line summary:")
        cons = cons[:cons_index+1]

    result = {"One_Line": one_line_summary,"Pros": pros, "Cons": cons}

    print(json.dumps(result, indent=4))
    reduceOneCredit(uid)
    return json.dumps(result, indent=4)
  except:
    result = {"One_Line": one_line_summary,"Pros": pros, "Cons": cons}
    print("Err")
    reduceOneCredit(uid)
    return json.dumps(result, indent=4)

@app.route('/getAIResponse', methods=['POST'])
def mainFunction():
    data = request.get_json()
    pw = data['website']
    pn = data['name']
    token = data['token']
    uid = extract_user_id(token)
    pa = data['asin']
    #pa = getASINNumner(urs)
    print(pa)
    user_data = root_ref.child('users').child(uid).get()
    # if user_data['credits'] <=0:
    #     return ""
    url = "https://"+pw+"/"+pn+"/product-reviews/"+pa+"/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
    soup = html_code(url)
    rs = cus_rev(soup)
    strs = ""
    for r in rs:
        strs = strs + r.replace("\n", "")

    tokes = num_tokens_from_string(strs, "gpt2")

    tokens = re.findall(r'\S+', strs)[:1600]
    print(tokens)
    final_text = " ".join(tokens)
    print(final_text)

    res = get_ai_response(final_text, uid)
    print(res)
    return res

@app.route('/getCredits', methods=['POST'])
def getCredits():
    data = request.get_json()
    token = data['token']
    uid = extract_user_id(token)
    user_data = root_ref.child('users').child(uid).get()

    return user_data
 
def RegisternewUser(uid):
    root_ref.child('users').child(uid).set({
            'credits': 5
    })

def extract_user_id(jwt_token):
    decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
    user_id = decoded_token['user_id']
    print(user_id)
    return user_id

def reduceOneCredit(idd):
    user_data = root_ref.child('users').child(idd).get()
    print(user_data["credits"])
    user_data["credits"] = user_data["credits"] - 1
    root_ref.child('users').child(idd).set({
            'credits': user_data["credits"]
    })

if __name__ == '__main__':
    app.run(port=80, host="0.0.0.0")
