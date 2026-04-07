from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_data(url):
    try:
        # 2-3 baar try karega agar fail hua toh
        for _ in range(2):
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.text
            time.sleep(1)
    except:
        return None
    return None

@app.route('/')
def home():
    return "FUNKEYY ENGINE IS RUNNING!"

@app.route('/mega-search', methods=['POST'])
def mega_search():
    query = request.json.get('query')
    if not query:
        return jsonify({"status": "error", "message": "No query"}), 400
    
    results = []
    
    # --- AMAZON SEARCH ---
    amz_html = fetch_data(f"https://www.amazon.in/s?k={query}")
    if amz_html:
        soup = BeautifulSoup(amz_html, 'html.parser')
        item = soup.find('div', {'data-component-type': 's-search-result'})
        if item:
            try:
                results.append({
                    "store": "Amazon",
                    "title": item.h2.text.strip()[:50] + "...",
                    "price": item.find('span', 'a-price-whole').text,
                    "img": item.find('img', 's-image')['src'],
                    "link": "https://www.amazon.in" + item.h2.a['href']
                })
            except: pass

    # --- FLIPKART SEARCH ---
    flip_html = fetch_data(f"https://www.flipkart.com/search?q={query}")
    if flip_html:
        soup = BeautifulSoup(flip_html, 'html.parser')
        # Sabse simple selector use kar rahe hain jo block kam hota hai
        cards = soup.find_all('div', recursive=True)
        for card in cards:
            price = card.find('div', string=lambda x: x and '₹' in x)
            if price and len(results) < 2: # Sirf ek result uthao
                results.append({
                    "store": "Flipkart",
                    "title": f"{query} on Flipkart",
                    "price": price.text.replace('₹', '').replace(',', ''),
                    "img": "https://static-assets-web.flixcart.com/fk-p-linchpin-web/fk-cp-zion/img/flipkart-plus_8d85f4.png",
                    "link": f"https://www.flipkart.com/search?q={query}"
                })
                break

    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run()
