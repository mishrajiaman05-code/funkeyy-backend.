from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Taaki Vercel aur Render aapas mein baat kar sakein

@app.route('/get-price', methods=['POST'])
def get_price():
    data = request.json
    url = data.get('url')
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5"
    }

    try:
        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Amazon Logic
        title = soup.find(id="productTitle").get_text().strip()
        # Price nikalne ke alag-alag tareeke (Amazon badalta rehta hai)
        price_span = soup.find("span", {"class": "a-price-whole"})
        price = price_span.text if price_span else "Check on Site"
        
        image_tag = soup.find(id="landingImage")
        image = image_tag['src'] if image_tag else "https://via.placeholder.com/150"

        return jsonify({
            "status": "success",
            "title": title[:60] + "...", 
            "price": price,
            "image": image
        })
    except Exception as e:
        return jsonify({"status": "error", "message": "Bhai, link sahi nahi hai ya Amazon ne block kiya!"})

if __name__ == '__main__':
    app.run()
