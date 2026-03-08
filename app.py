from flask import Flask, request, jsonify
from ai_module import generate_ai_tags
from database import init_db, save_product
import os

app = Flask(__name__)

# Initialize database
init_db()


# Home route
@app.route("/")
def home():
    return """
    <h2>AI Catalog Generator Server Running</h2>
    <p>Use this link to test:</p>
    <a href="/generate">Open Generator Form</a>
    """


# Generate endpoint
@app.route("/generate", methods=["GET", "POST"])
def generate():

    # Show HTML form
    if request.method == "GET":
        return """
        <h3>AI Product Category Generator</h3>

        <form method="POST">
        Product Name:<br>
        <input name="name"><br><br>

        Description:<br>
        <textarea name="description"></textarea><br><br>

        <button type="submit">Generate</button>
        </form>
        """

    # Handle POST request
    if request.is_json:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
    else:
        name = request.form.get("name")
        description = request.form.get("description")

    # Validate input
    if not name or not description:
        return jsonify({"error": "Product name and description required"}), 400

    # Generate AI tags
    ai = generate_ai_tags(name, description)

    # Save product in database
    save_product(
        name,
        ai["category"],
        ai["subcategory"],
        ai["seo_tags"],
        ai["sustainability"]
    )

    return jsonify(ai)


if __name__ == "__main__":
    print("Starting AI Catalog Server...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)