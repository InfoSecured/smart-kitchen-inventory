import sqlite3

DB_FILE = "barcode_cache.db"

def init_cache():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS barcode_cache (
        barcode TEXT PRIMARY KEY,
        product_data TEXT
    )''')
    conn.commit()
    conn.close()

def save_product(barcode, product_data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO barcode_cache (barcode, product_data) VALUES (?, ?)", (barcode, str(product_data)))
    conn.commit()
    conn.close()

def get_cached_product(barcode):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT product_data FROM barcode_cache WHERE barcode = ?", (barcode,))
    result = c.fetchone()
    conn.close()
    return eval(result[0]) if result else None