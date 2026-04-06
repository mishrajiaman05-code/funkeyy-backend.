from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

def search_amazon(query):
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        # Pehla product uthao
        item = soup.find("div", {"data-component-type": "s-search-result"})
        title = item.find("h2").text.strip()
        price = item.find("span", {"class": "a-price-whole"}).text
        link = "https://www.amazon.in" + item.find("a", {"class": "a-link-normal"})['href']
        img = item.find("img", {"class": "s-image"})['src']
        return {"store": "Amazon", "title": title[:50], "price": price, "link": link, "img": img}
    except: return None

def search_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        # Flipkart layout checking
        item = soup.find("div", {"class": "_1AtVbE"}) or soup.find("div", {"class": "_4ddWXP"})
        title = item.find("div", {"class": "_4rR01T"}) or item.find("a", {"class": "s1Q9rs"})
        price = item.find("div", {"class": "_30jeq3"})
        img = item.find("img")['src']
        link = "https://www.flipkart.com" + item.find("a")['href']
        return {"store": "Flipkart", "title": title.text[:50], "price": price.text.replace("₹",""), "link": link, "img": img}
    except: return None

@app.route('/mega-search', methods=['POST'])
def mega_search():
    query = request.json.get('query')
    results = []
    
    amz = search_amazon(query)
    if amz: results.append(amz)
    
    fk = search_flipkart(query)
    if fk: results.append(fk)
    
    return jsonify({"status": "success", "data": results})

if __name__ == '__main__':
    app.run()
