from flask import Flask,request, jsonify
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
@app.route("/", methods=['GET'])
def testroute():
    return "<h1> This message verifies the summarization server is running publicly in the doc.gold.ac.uk domain</h1>"

@app.route("/summarization", methods=['POST'])
def summarization():
    req_json = request.get_json()
    user_id = req_json.get('userID')
    whole_text =  req_json.get('wholeText')
    summarized_text, text_keywords = performSummarization(whole_text) 
    summaryObject = {'summary':summarized_text, 'keywords':text_keywords}
    resulting_path_to_summary = sendSummaryToFirebase(user_id,summaryObject)
    response = jsonify(resulting_path_to_summary)
    response.status_code = 200
    return response
# =========== HELPER FUNCTIONS ========

def sendSummaryToFirebase(uid,summaryObject):
    # usersSummaries
    dbRef = db.reference('usersSummaries')
    thisUser = dbRef.child('{}'.format(uid))
    if thisUser is None:
        newSummary = db.reference('usersSummaries/{}'.format(uid)).push(summaryObject)
    else:
        newSummary = thisUser.push(summaryObject)
    pathToNewSummary = 'usersSummaries/{}/{}'.format(uid,newSummary.key)
    
    return pathToNewSummary

def performSummarization(text):
    summarization = summarize(text, ratio=0.2)
    text_keywords = keywords(text, ratio=0.2)
    return summarization,text_keywords

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=443,debug=True)
