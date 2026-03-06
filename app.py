from flask import Flask, request, jsonify
from ai_module import generate_ai_tags
from database import init_db, save_product

app = Flask(__name__)

# Initialize database
init_db()


# Home route so browser does not show Not Found
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

    # Show simple HTML form
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

    # POST request
    if request.is_json:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
    else:
        name = request.form.get("name")
        description = request.form.get("description")

    # Generate AI tags
    ai = generate_ai_tags(name, description)

    # Save to database
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
    print("Open browser: http://127.0.0.1:5000")
    print("Test form: http://127.0.0.1:5000/generate")

    app.run(debug=True)