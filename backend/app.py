import os
import uuid
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

# --- Initialization ---
load_dotenv()
app = Flask(__name__)

# UPDATED: Configure CORS to specifically allow your Netlify frontend URL
CORS(app, resources={r"/api/*": {"origins": "https://aidea-board.netlify.app"}})


# --- Firebase Setup ---
try:
    SERVICE_ACCOUNT_KEY_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
    if not SERVICE_ACCOUNT_KEY_PATH:
        raise ValueError("FIREBASE_SERVICE_ACCOUNT_KEY_PATH not set in .env")
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firestore initialized successfully.")
except Exception as e:
    print(f"Error initializing Firestore: {e}")
    db = None

# --- Google AI Setup (FINAL STABLE VERSION) ---
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in .env")
# FINAL FIX: Using the v1beta endpoint with a stable model is the most reliable method.
AI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_API_KEY}"
print("Google AI Direct API URL is configured with the final stable endpoint.")

DEMO_USER_ID = "user123"

def get_board_ref(user_id):
    return db.collection('boards').document(user_id)

def get_initial_board_data():
    card_id_1 = str(uuid.uuid4())
    return {
        "cards": { card_id_1: {"id": card_id_1, "content": "Welcome! Drag this card or create a new one."}},
        "columns": {
            "col-1": {"id": "col-1", "title": "To Do", "cardIds": [card_id_1]},
            "col-2": {"id": "col-2", "title": "In Progress", "cardIds": []},
            "col-3": {"id": "col-3", "title": "Done", "cardIds": []}
        }, "columnOrder": ["col-1", "col-2", "col-3"],
    }

# --- API ROUTES ---
@app.route('/api/board', methods=['GET'])
def get_board():
    if not db: return jsonify({"error": "Database not initialized"}), 500
    try:
        doc = get_board_ref(DEMO_USER_ID).get()
        if doc.exists: return jsonify(doc.to_dict())
        else:
            initial_data = get_initial_board_data()
            get_board_ref(DEMO_USER_ID).set(initial_data)
            return jsonify(initial_data)
    except Exception as e:
        print(f"Error getting board: {e}")
        return jsonify({"error": "Could not retrieve board data"}), 500

@app.route('/api/board', methods=['POST'])
def update_board():
    if not db: return jsonify({"error": "Database not initialized"}), 500
    try:
        get_board_ref(DEMO_USER_ID).set(request.json)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error updating board: {e}")
        return jsonify({"error": "Could not update board"}), 500

# --- AI ROUTES (REWRITTEN FOR STABILITY) ---
def call_generative_ai(prompt):
    """A single, stable function to call the AI via direct HTTP request with better error logging."""
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(AI_API_URL, headers=headers, json=payload)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
        raise http_err
    except Exception as e:
        print(f"An unexpected error occurred in call_generative_ai: {e}")
        raise e


@app.route('/api/ai/suggest', methods=['POST'])
def get_suggestions():
    try:
        prompt = f"Based on the idea '{request.json['text']}', generate 3 very short, creative, related brainstorming ideas. Return them as a simple list separated by commas, with no numbering. Example: Idea A, Idea B, Idea C"
        result = call_generative_ai(prompt)
        if 'candidates' in result and len(result['candidates']) > 0:
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify([s.strip() for s in text_response.split(',') if s.strip()])
        else:
            print("AI response did not contain candidates:", result)
            return jsonify({"error": "Invalid response from AI"}), 500
    except Exception as e:
        print(f"AI suggestion error: {e}")
        return jsonify({"error": "Failed to get AI suggestions"}), 500

@app.route('/api/ai/summarize', methods=['POST'])
def get_summary():
    try:
        all_text = ". ".join(request.json.get('cards', []))
        if not all_text:
            return jsonify({"summary": "Add some cards to get a summary!"})
        prompt = f"Summarize the key themes from these brainstorming notes in 2-3 concise bullet points:\n\n{all_text}"
        result = call_generative_ai(prompt)
        summary = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"summary": summary})
    except Exception as e:
        print(f"AI summary error: {e}")
        return jsonify({"error": "Failed to generate summary"}), 500

@app.route('/api/ai/visualize', methods=['POST'])
def get_visualization():
    try:
        placeholder_url = f"https://picsum.photos/600/400?random={uuid.uuid4()}"
        return jsonify({"imageData": placeholder_url})
    except Exception as e:
        print(f"Visualization placeholder error: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/api/ai/cluster', methods=['POST'])
def cluster_ideas():
    try:
        cards = request.json.get('cards', {})
        if len(cards) < 3: return jsonify({"clusters": {}})
        ids, texts = zip(*cards.items())
        vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
        X = vectorizer.fit_transform(texts)
        num_clusters = min(len(ids), 4)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10).fit(X)
        clusters = {ids[i]: int(kmeans.labels_[i]) for i in range(len(ids))}
        return jsonify({"clusters": clusters})
    except Exception as e:
        print(f"Clustering error: {e}")
        return jsonify({"error": "Failed to cluster ideas"}), 500

if __name__ == '__main__':
    app.run(debug=True)