from flask import Flask, request
from ai_module import generate_ai_tags
from database import init_db, save_product
import os

app = Flask(__name__)

# initialize database
init_db()


# Home route
@app.route("/")
def home():
    return """
    <h2>AI Catalog Generator Server Running</h2>
    <p>Click below to test the generator</p>
    <a href="/generate">Open Generator</a>
    """


# Generator route
@app.route("/generate", methods=["GET", "POST"])
def generate():

    # Show form
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

    # Get form data
    name = request.form.get("name")
    description = request.form.get("description")

    if not name or not description:
        return "<h3>Please enter product name and description</h3>"

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

    # Show result nicely
    return f"""
    <h2>AI Generated Product Details</h2>

    <b>Category:</b> {ai["category"]}<br><br>

    <b>Subcategory:</b> {ai["subcategory"]}<br><br>

    <b>SEO Tags:</b> {", ".join(ai["seo_tags"])}<br><br>

    <b>Sustainability:</b> {", ".join(ai["sustainability"]) if ai["sustainability"] else "None"}<br><br>

    <a href="/generate">Generate Another Product</a>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)