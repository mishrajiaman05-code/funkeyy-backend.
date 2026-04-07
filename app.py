from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# --- ASLI USER AGENT ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

def get_amazon(query):
    try:
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Amazon search results find karne ka naya tarika
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        for item in items:
            title_el = item.find('h2')
            price_el = item.find('span', 'a-price-whole')
            img_el = item.find('img', 's-image')
            
            if title_el and price_el:
                return {
                    "store": "Amazon",
                    "title": title_el.text.strip()[:50] + "...",
                    "price": price_el.text,
                    "img": img_el['src'] if img_el else "",
                    "link": "https://www.amazon.in" + title_el.a['href']
                }
    except: return None

def get_flipkart(query):
    try:
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Flipkart Multi-layout support (Grid and List)
        # 1. Mobile/Laptop layout
        item = soup.find('div', {'class': '_1AtV32'}) or soup.find('div', {'class': 'sl_Z_m'})
        if item:
            title = item.find('div', {'class': '_4rR01T'}) or item.find('a', {'class': 'IRpwBC'})
            price = item.find('div', {'class': '_30jeq3'})
            img = item.find('img', {'class': '_396cs4'}) or item.find('img', {'class': '_2r_T1I'})
            link = item.find('a', {'class': '_1fQZEK'}) or item.find('a', {'class': 'IRpwBC'})
            
            if title and price:
                return {
                    "store": "Flipkart",
                    "title": title.text.strip()[:50] + "...",
                    "price": price.text.replace('₹', '').replace(',', ''),
                    "img": img['src'] if img else "",
                    "link": "https://www.flipkart.com" + (link['href'] if link.has_attr('href') else "")
                }
    except: return None

@app.route('/')
def home(): return "FUNKEYY v5.0 IS LIVE!"

@app.route('/mega-search', methods=['POST'])
def mega_search():
    query = request.json.get('query')
    if not query: return jsonify({"status": "error"}), 400
    
    results = []
    amz = get_amazon(query)
    flp = get_flipkart(query)
    
    if amz: results.append(amz)
    if flp: results.append(flp)
    
    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run()
