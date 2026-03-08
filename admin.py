import os
import json
import subprocess
from flask import Flask, render_template, request, jsonify

os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
FEEDS_FILE = "feeds.json"
MAX_FEEDS = 10

DEFAULT_FEEDS = [
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "name": "TechCrunch", "max_items": 5},
    {"url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "name": "The Verge", "max_items": 5},
    {"url": "https://venturebeat.com/category/ai/feed/", "name": "VentureBeat", "max_items": 5},
    {"url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "name": "MIT Technology Review", "max_items": 5},
    {"url": "https://www.theguardian.com/technology/artificialintelligenceai/rss", "name": "The Guardian", "max_items": 5},
    {"url": "https://www.artificialintelligence-news.com/feed/", "name": "AI News", "max_items": 5},
]

def load_feeds():
    if not os.path.exists(FEEDS_FILE):
        save_feeds(DEFAULT_FEEDS)
        return DEFAULT_FEEDS
    with open(FEEDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_feeds(feeds):
    with open(FEEDS_FILE, "w", encoding="utf-8") as f:
        json.dump(feeds, f, ensure_ascii=False, indent=2)

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/api/feeds", methods=["GET"])
def get_feeds():
    return jsonify(load_feeds())

@app.route("/api/feeds", methods=["POST"])
def add_feed():
    feeds = load_feeds()
    if len(feeds) >= MAX_FEEDS:
        return jsonify({"error": f"最大{MAX_FEEDS}サイトまでです"}), 400
    data = request.json
    url = data.get("url", "").strip()
    name = data.get("name", "").strip()
    max_items = int(data.get("max_items", 5))
    if not url:
        return jsonify({"error": "URLは必須です"}), 400
    if any(f["url"] == url for f in feeds):
        return jsonify({"error": "既に登録されているURLです"}), 400
    feeds.append({"url": url, "name": name or url, "max_items": max_items})
    save_feeds(feeds)
    return jsonify({"ok": True})

@app.route("/api/feeds/<int:idx>", methods=["PUT"])
def update_feed(idx):
    feeds = load_feeds()
    if idx < 0 or idx >= len(feeds):
        return jsonify({"error": "対象が見つかりません"}), 404
    data = request.json
    feeds[idx]["url"] = data.get("url", feeds[idx]["url"]).strip()
    feeds[idx]["name"] = data.get("name", feeds[idx]["name"]).strip()
    feeds[idx]["max_items"] = int(data.get("max_items", feeds[idx]["max_items"]))
    save_feeds(feeds)
    return jsonify({"ok": True})

@app.route("/api/feeds/<int:idx>", methods=["DELETE"])
def delete_feed(idx):
    feeds = load_feeds()
    if idx < 0 or idx >= len(feeds):
        return jsonify({"error": "対象が見つかりません"}), 404
    feeds.pop(idx)
    save_feeds(feeds)
    return jsonify({"ok": True})

@app.route("/api/reload", methods=["POST"])
def reload_news():
    try:
        result = subprocess.Popen(
            ["python3", "update_news.py"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        return jsonify({"ok": True, "pid": result.pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5501, debug=False)