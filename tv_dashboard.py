import requests
import json
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# TMDB API Read Access Token
TMDB_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxOWNhNzUyYjRmMTVhMzE0NjBjMjhmZGRmNmUyMGVlNyIsIm5iZiI6MTY0MzQ1MDgwMy44MTcsInN1YiI6IjYxZjUxMWIzMDI4NDIwMDA5NDVjZTYzMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.whaF_oCk9NmW5zsIGIRORek1mBZIALUI9AMOvgvmd0w"
TV_SHOW_IDS = [208569, 214162, 250307, 95396, 255055, 208397, 138503, 117488, 95557]  # Replace with your TV series IDs

def format_date(date_str):
    """Convert TMDB's YYYY-MM-DD format to a more readable format."""
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
        except ValueError:
            return date_str  # If parsing fails, return original string
    return "Unknown"

def fetch_episode_data():
    episodes = []
    headers = {"Authorization": f"Bearer {TMDB_API_TOKEN}"}

    for tv_id in TV_SHOW_IDS:
        url = f"https://api.themoviedb.org/3/tv/{tv_id}?append_to_response=next_episode_to_air,last_episode_to_air"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            show_name = data.get("name", "Unknown Show")

            last_episode = data.get("last_episode_to_air", {})
            next_episode = data.get("next_episode_to_air", {})

            episodes.append({
                "id": tv_id,
                "name": show_name,
                "poster_url": f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}",
                "last_episode": {
                    "season": last_episode.get("season_number", "-"),
                    "episode": last_episode.get("episode_number", "-"),
                    "title": last_episode.get("name", "N/A"),
                    "air_date": format_date(last_episode.get("air_date")),
                },
                "next_episode": {
                    "season": next_episode.get("season_number", "-"),
                    "episode": next_episode.get("episode_number", "-"),
                    "title": next_episode.get("name", "N/A"),
                    "air_date": format_date(next_episode.get("air_date")),
                },
                "tmdb_link": f"https://www.themoviedb.org/tv/{tv_id}"
            })

    return episodes

@app.route("/")
def dashboard():
    episodes = fetch_episode_data()
    return render_template("dashboard.html", episodes=episodes)

@app.route("/update")
def update_data():
    episodes = fetch_episode_data()
    return jsonify({"status": "updated", "episodes": episodes})

if __name__ == "__main__":
    app.run(debug=True)
