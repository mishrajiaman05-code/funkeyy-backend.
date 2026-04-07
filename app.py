from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import random

app = Flask(__name__)
CORS(app)

# --- MULTIPLE USER AGENTS TAAKI BLOCK NA HO ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

@app.route('/')
def home():
    return "FUNKEYY ENGINE IS RUNNING!"

@app.route('/mega-search', methods=['POST'])
def mega_search():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({"status": "error", "message": "Query missing"}), 400

    results = []
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    # --- 🛒 AMAZON LOGIC ---
    try:
        amz_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        res = requests.get(amz_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Sasta aur pakka selector
        card = soup.find('div', {'data-component-type': 's-search-result'})
        if card:
            title = card.h2.text.strip()[:60] + "..."
            price = card.find('span', 'a-price-whole').text
            img = card.find('img', 's-image')['src']
            link = "https://www.amazon.in" + card.h2.a['href']
            results.append({"store": "Amazon", "title": title, "price": price, "img": img, "link": link})
    except Exception as e:
        print(f"Amazon Error: {e}")

    # --- 🛒 FLIPKART LOGIC ---
    try:
        flip_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
        res = requests.get(flip_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Flipkart Search Card
        item = soup.find('div', {'class': '_1AtV32'}) or soup.find('div', {'class': 'sl_Z_m'})
        if item:
            title_el = item.find('div', {'class': '_4rR01T'}) or item.find('a', {'class': 'IRpwBC'})
            price_el = item.find('div', {'class': '_30jeq3'})
            img_el = item.find('img', {'class': '_396cs4'}) or item.find('img', {'class': '_2r_T1I'})
            link_el = item.find('a', {'class': '_1fQZEK'}) or item.find('a', {'class': 'IRpwBC'})
            
            if title_el and price_el:
                results.append({
                    "store": "Flipkart",
                    "title": title_el.text[:60] + "...",
                    "price": price_el.text.replace('₹', '').replace(',', ''),
                    "img": img_el['src'] if img_el else "",
                    "link": "https://www.flipkart.com" + link_el['href']
                })
    except Exception as e:
        print(f"Flipkart Error: {e}")

    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run()
