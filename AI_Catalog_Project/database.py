import sqlite3
import json


def init_db(db_path: str = "products.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        subcategory TEXT,
        tags TEXT,
        sustainability TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_product(name, category, subcategory, tags, sustainability, db_path: str = "products.db"):
    """Save a product. `tags` and `sustainability` may be lists; they are stored as JSON strings.

    Args:
        name (str): product name
        category (str)
        subcategory (str)
        tags (list or str): list of tags or JSON/text
        sustainability (list or str): list of sustainability labels or JSON/text
        db_path (str): path to sqlite db file
    """
    if not isinstance(tags, str):
        tags = json.dumps(tags)
    if not isinstance(sustainability, str):
        sustainability = json.dumps(sustainability)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO products(name,category,subcategory,tags,sustainability)
    VALUES (?,?,?,?,?)
    """, (name, category, subcategory, tags, sustainability))

    conn.commit()
    conn.close()