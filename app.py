from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.route('/')
def home():
    return "SYSTEM ONLINE: MUZAFFARPUR EDITION v5.1"

@app.route('/mega-search', methods=['POST'])
def mega_search():
    query = request.json.get('query', '')
    if not query:
        return jsonify({"status": "error"}), 400

    results = []

    # --- JUGAD: GOOGLE SEARCH SE PRICE NIKALNA ---
    # Hum Google pe search karenge "site:amazon.in [query]"
    def get_price_via_google(site_name, site_domain):
        try:
            search_url = f"https://www.google.com/search?q=site:{site_domain}+{query}"
            res = requests.get(search_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Google ke search snippet se price dhundna
            text = soup.get_text()
            price_match = re.search(r'₹\s?([0-9,]+)', text)
            
            if price_match:
                return {
                    "store": site_name,
                    "title": f"{query} on {site_name}",
                    "price": price_match.group(1),
                    "img": "https://cdn-icons-png.flaticon.com/512/2331/2331970.png", # Default Icon
                    "link": f"https://www.google.com/search?q={site_domain}+{query}"
                }
        except:
            return None

    # Amazon check
    amz = get_price_via_google("Amazon", "amazon.in")
    if amz: results.append(amz)

    # Flipkart check
    flp = get_price_via_google("Flipkart", "flipkart.com")
    if flp: results.append(flp)

    # Agar Google se bhi kuch nahi mila (Extreme Case)
    if not results:
        # Dummy data bhej rahe hain taaki tera UI "Empty" na dikhe
        results.append({
            "store": "System Check",
            "title": f"Checking best deals for {query}...",
            "price": "Live Scan",
            "img": "https://cdn-icons-png.flaticon.com/512/1055/1055644.png",
            "link": "#"
        })

    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run()
