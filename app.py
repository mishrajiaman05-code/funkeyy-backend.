from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app) # Ye line frontend ko connect karne ke liye zaroori hai

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

@app.route('/')
def home():
    return "FUNKEYY Backend is LIVE! v5.0 Muzaffarpur Edition"

@app.route('/mega-search', methods=['POST'])
def mega_search():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"status": "error", "message": "Bhai query missing hai"}), 400
    
    results = []
    
    # --- AMAZON SCRAPER ---
    try:
        amz_url = f"https://www.amazon.in/s?k={query}"
        res = requests.get(amz_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        item = soup.find('div', {'data-component-type': 's-search-result'})
        if item:
            results.append({
                "store": "Amazon",
                "title": item.h2.text.strip()[:50] + "...",
                "price": item.find('span', 'a-price-whole').text,
                "img": item.find('img', 's-image')['src'],
                "link": "https://www.amazon.in" + item.h2.a['href']
            })
    except Exception as e:
        print(f"Amazon Error: {e}")

    # --- FLIPKART SCRAPER ---
    try:
        flip_url = f"https://www.flipkart.com/search?q={query}"
        res = requests.get(flip_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Common class for Flipkart product cards
        item = soup.find('div', {'class': '_1AtV32'}) or soup.find('div', {'class': 'sl_Z_m'})
        if item:
            title = item.find('div', {'class': '_4rR01T'}) or item.find('a', {'class': 'IRpwBC'})
            price = item.find('div', {'class': '_30jeq3'})
            img = item.find('img', {'class': '_396cs4'}) or item.find('img', {'class': '_2r_T1I'})
            link = item.find('a', {'class': '_1fQZEK'}) or item.find('a', {'class': 'IRpwBC'})
            
            if title and price:
                results.append({
                    "store": "Flipkart",
                    "title": title.text.strip()[:50] + "...",
                    "price": price.text.replace('₹', '').replace(',', ''),
                    "img": img['src'] if img else "",
                    "link": "https://www.flipkart.com" + link['href'] if link else "#"
                })
    except Exception as e:
        print(f"Flipkart Error: {e}")

    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run()
