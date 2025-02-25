from flask import Flask, redirect, jsonify
import random
import string
app = Flask(__name__)

# In-memory storage
url_database = {}

def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=4))

@app.route('/')
def home():
    return "URL Shortener is running!"

@app.route('/create/<path:url>')
def create_short_url(url):
    short_code = generate_short_code()
    url_database[short_code] = url
    return jsonify({
        "original_url": url,
        "short_code": short_code,
        "short_url": f"http://localhost:5000/{short_code}"
    })

@app.route('/<short_code>')
def redirect_url(short_code):
    long_url = url_database.get(short_code)
    if long_url:
        return redirect(long_url)
    return jsonify({"error": "URL not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
