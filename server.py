from flask import Flask,request
app = Flask(__name__)

import gensim
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
from flask_cors import CORS

# ========== INITIALISE AND CONNECT WITH THE ULA FIREBASE ACCOUNT =========
import firebase_admin
from firebase_admin import credentials,db, auth

cred = credentials.Certificate('firebase_admin_key/ultimate-listening-assistant-firebase-adminsdk-znu10-1e553fa212.json')
# Initialize the app with a service account, granting admin privileges
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ultimate-listening-assistant.firebaseio.com/'
})

# =========== ENABLE CORS ==========
# TODO: REMEMBER TO RESTRICT CORS TO ONLY SPECIFIC DOMAINS (NOT ALL LIKE NOW)!
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# =========== ROUTES ==========
@app.route("/summarization", methods=['POST'])
def summarization():
    req_json = request.get_json()
    user_id = req_json.get('userID')
    whole_text =  req_json.get('wholeText')
    summarized_text, text_keywords = performSummarization(whole_text) 
    summaryObject = {'summary':summarized_text, 'keywords':text_keywords}
    return sendSummaryToFirebase(user_id,summaryObject)

# =========== HELPER FUNCTIONS ========

def sendSummaryToFirebase(uid,summaryObject):
    # usersSummaries
    dbRef = db.reference(f'usersSummaries')
    thisUser = dbRef.child(f'{uid}')
    if thisUser is None:
        newSummary = db.reference(f'usersSummaries/{uid}').push(summaryObject)
    else:
        newSummary = thisUser.push(summaryObject)
    pathToNewSummary = f'usersSummaries/{uid}/{newSummary.key}'
    return pathToNewSummary

def performSummarization(text):
    summarization = summarize(text, ratio=0.2)
    print("this is the summarization")
    print(summarization)
    text_keywords = keywords(text, ratio=0.2)
    return summarization,text_keywords

if __name__ == '__main__':
    app.run(debug=True)