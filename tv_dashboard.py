from flask import Flask, render_template, jsonify
import requests
import json
import datetime

# TMDB API Configuration
TMDB_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxOWNhNzUyYjRmMTVhMzE0NjBjMjhmZGRmNmUyMGVlNyIsIm5iZiI6MTY0MzQ1MDgwMy44MTcsInN1YiI6IjYxZjUxMWIzMDI4NDIwMDA5NDVjZTYzMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.whaF_oCk9NmW5zsIGIRORek1mBZIALUI9AMOvgvmd0w"
TV_SERIES_IDS = [208569, 214162, 250307, 95396, 255055, 208397, 138503]  # Replace with the TV series IDs you want to track
HEADERS = {"Authorization": f"Bearer {TMDB_ACCESS_TOKEN}"}
TMDB_URL = "https://api.themoviedb.org/3/tv/{}"

# JSON file to store episode data
DATA_FILE = "dashboard_data.json"

app = Flask(__name__)

def load_episode_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_episode_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def get_latest_episode(tv_id):
    url = TMDB_URL.format(tv_id)
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        last_episode = data.get("last_episode_to_air")
        if last_episode:
            return {
                "tv_id": tv_id,
                "name": data["name"],
                "season": last_episode["season_number"],
                "episode": last_episode["episode_number"],
                "title": last_episode["name"],
                "air_date": last_episode["air_date"],
                "poster_url": f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
                "tmdb_link": f"https://www.themoviedb.org/tv/{tv_id}"
            }
    return None

@app.route("/")
def dashboard():
    episodes = load_episode_data()
    return render_template("dashboard.html", episodes=episodes)

@app.route("/update")
def update_data():
    episode_list = []
    for tv_id in TV_SERIES_IDS:
        episode = get_latest_episode(tv_id)
        if episode:
            episode_list.append(episode)
    
    save_episode_data(episode_list)
    return jsonify({"status": "updated", "episodes": episode_list})

if __name__ == "__main__":
    with app.app_context():  # Ensure it's within Flask's context
        update_data()  # Fetch initial data
    app.run(debug=True)