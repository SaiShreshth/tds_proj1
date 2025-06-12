from flask import Flask, request, jsonify
import openai
import your_vector_search_module  # You'll create this

openai.api_key = "YOUR_OPENAI_KEY"

app = Flask(__name__)

@app.route("/api/", methods=["POST"])
def virtual_ta():
    data = request.get_json()
    question = data.get("question", "")
    image_data = data.get("image", None)
    image_text = ""

    context, links = your_vector_search_module.search(question + " " + image_text)

    messages = [{"role": "system", "content": "Answer the question using the course and Discourse data."},
                {"role": "user", "content": f"Q: {question}\n\nContext:\n{context}"}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        temperature=0.2
    )

    return jsonify({
        "answer": response.choices[0].message.content,
        "links": links
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)