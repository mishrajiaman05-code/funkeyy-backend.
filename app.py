from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

def search_amazon(query):
    url = f"https://www.amazon.in/s?k={query}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        item = soup.find('div', {'data-component-type': 's-search-result'})
        if item:
            return {
                "store": "Amazon",
                "title": item.h2.text.strip()[:50] + "...",
                "price": item.find('span', 'a-price-whole').text,
                "img": item.find('img', 's-image')['src'],
                "link": "https://www.amazon.in" + item.h2.a['href']
            }
    except: return None

def search_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # This logic is for mobiles/electronics on Flipkart
        item = soup.find('div', {'class': '_1AtV32'}) 
        if item:
            title = item.find('div', {'class': '_4rR01T'})
            price = item.find('div', {'class': '_30jeq3'})
            img = item.find('img', {'class': '_396cs4'})
            link = item.find('a', {'class': '_1fQZEK'})
            if title and price:
                return {
                    "store": "Flipkart",
                    "title": title.text.strip()[:50] + "...",
                    "price": price.text.replace('₹', ''),
                    "img": img['src'],
                    "link": "https://www.flipkart.com" + link['href']
                }
    except: return None

@app.route('/mega-search', methods=['POST'])
def mega_search():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"status": "error", "message": "No query"}), 400
    
    results = []
    amz = search_amazon(query)
    flp = search_flipkart(query)
    
    if amz: results.append(amz)
    if flp: results.append(flp)
    
    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run()
