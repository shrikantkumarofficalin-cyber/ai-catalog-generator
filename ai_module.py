import os
import json

try:
    import openai
except Exception:
    openai = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def generate_ai_tags(product, description):
    """Generate AI tags. If OpenAI credentials are not available, return a mock response.

    Returns a dict with keys: category, subcategory, seo_tags (list), sustainability (list).
    """
    # Predefined category list and simple keyword mapping for deterministic classification
    CATEGORIES = [
        "Home", "Electronics", "Clothing", "Beauty", "Toys", "Sports", "Food",
        "Health", "Garden", "Books", "Accessories", "Misc"
    ]

    KEYWORD_CATEGORY_MAP = {
        "t-shirt": "Clothing",
        "shirt": "Clothing",
        "shoe": "Clothing",
        "sneaker": "Clothing",
        "phone": "Electronics",
        "charger": "Electronics",
        "lamp": "Home",
        "sofa": "Home",
        "shampoo": "Beauty",
        "toy": "Toys",
        "ball": "Sports",
        "book": "Books",
        "tea": "Food",
        "coffee": "Food",
        "plant": "Garden",
        "skincare": "Beauty",
    }

    SUSTAINABILITY_KEYWORDS = [
        "recycled", "recyclable", "plastic-free", "compostable", "biodegradable",
        "vegan", "organic", "fair trade", "cruelty-free", "eco-friendly", "sustainable"
    ]

    def local_classify(name, desc):
        text = f"{name} {desc}".lower()
        # category
        for k, v in KEYWORD_CATEGORY_MAP.items():
            if k in text:
                category = v
                break
        else:
            category = "Misc"

        # subcategory heuristic: pick a nearby word from name if any
        subcategory = "General"
        words = [w.strip(".,") for w in (name or "").split()]
        if words:
            candidate = words[0].lower()
            if len(candidate) > 2:
                subcategory = candidate.capitalize()

        # SEO tags: extract words, remove short/stopwords, and pick top unique tokens
        stopwords = set([
            "and", "or", "the", "a", "an", "with", "for", "in", "on", "of", "to",
            "by", "is", "it", "this", "that"
        ])
        tokens = []
        for part in (name or "").split() + (description or "").split():
            t = ''.join(ch for ch in part.lower() if ch.isalnum())
            if not t or t in stopwords or len(t) < 3:
                continue
            tokens.append(t)

        # frequency ranking
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1

        sorted_tokens = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
        seo_tags = [t for t, _ in sorted_tokens]
        # include product name tokens first, then fill from description
        if not seo_tags:
            seo_tags = [w for w in (name or "").split() if len(w) > 2]
            seo_tags = [s.lower().strip('.,') for s in seo_tags][:5]

        # ensure 5-10 tags
        seo_tags = list(dict.fromkeys(seo_tags))  # unique preserve order
        if len(seo_tags) < 5:
            # add generic tags
            extras = ["best", "buy", "shop", "online", "new"]
            for e in extras:
                if e not in seo_tags:
                    seo_tags.append(e)
                if len(seo_tags) >= 5:
                    break
        if len(seo_tags) > 10:
            seo_tags = seo_tags[:10]

        # sustainability labels
        sustainability = []
        for kw in SUSTAINABILITY_KEYWORDS:
            if kw in text:
                sustainability.append(kw)

        # common inference if none found
        if not sustainability:
            # infer from description words
            if any(w in text for w in ["recycle", "recycled", "biodegradable", "compost", "vegan"]):
                sustainability.append("eco-friendly")

        return {
            "category": category,
            "subcategory": subcategory,
            "seo_tags": seo_tags,
            "sustainability": sustainability or []
        }

    # If OpenAI is configured, try using it but fall back to deterministic local method on any error.
    if openai and OPENAI_API_KEY:
        try:
            prompt = f"""
            Product Name: {product}\nDescription: {description}\n\nReturn JSON with keys: category, subcategory, seo_tags (list of 5-10), sustainability (list).\nOnly return valid JSON.\n"""

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            result = response['choices'][0]['message']['content']
            parsed = json.loads(result)
            # normalize to expected keys and types
            return {
                "category": parsed.get("category", "Misc"),
                "subcategory": parsed.get("subcategory", "General"),
                "seo_tags": parsed.get("seo_tags", [])[:10],
                "sustainability": parsed.get("sustainability", [])
            }
        except Exception:
            # fall back to local deterministic classifier
            return local_classify(product, description)

    # No OpenAI available — use deterministic local classifier
    return local_classify(product, description)