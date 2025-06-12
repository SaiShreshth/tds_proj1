from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os,requests

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

# Load filtered posts
with open("tds_discourse_filtered.json", "r", encoding="utf-8") as f:
    discourse_data = json.load(f)

# Load SentenceTransformer model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Precompute embeddings
corpus = [p["content"] for p in discourse_data]
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

def search_relevant_chunks(query, top_k=3):
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    scores = cosine_similarity([query_embedding], corpus_embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = [discourse_data[i] for i in top_indices]
    return results


load_dotenv()  # ✅ Load .env variables

app = Flask(__name__)

AI_PIPE_API_KEY = os.getenv("AIPIPE_API_KEY")  # Store your key in .env
AI_PIPE_API_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_PIPE_MODEL = "mistralai/mixtral-8x7b"

@app.route("/api/", methods=["POST"])
def virtual_ta():
    try:
        user_question = request.form.get("question")
        top_chunks = search_relevant_chunks(user_question, top_k=3)

        context = "\n---\n".join(chunk["text"] for chunk in top_chunks)
        messages = [
            {"role": "system", "content": "You are a helpful teaching assistant for the TDS course."},
            {"role": "user", "content": f"{user_question}\n\nUse this context:\n{context}"}
        ]

        headers = {
            "Authorization": f"Bearer {AI_PIPE_API_KEY}",
            "HTTP-Referer": "https://yourdomain.com",  # Can be localhost if needed
            "Content-Type": "application/json"
        }

        payload = {
            "model": AI_PIPE_MODEL,
            "messages": messages,
            "temperature": 0.2
        }

        res = requests.post(AI_PIPE_API_URL, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        reply = data["choices"][0]["message"]["content"]
        return jsonify({"answer": reply})

    except Exception as e:
        print("[!] Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)