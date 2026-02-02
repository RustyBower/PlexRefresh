import os
from urllib.parse import urlencode, quote

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

PLEX_URL = os.environ.get("PLEX_URL", "").rstrip("/")
PLEX_TOKEN = os.environ.get("PLEX_TOKEN", "")


def plex_request(endpoint, params=None):
    """Make a request to the Plex API."""
    if params is None:
        params = {}
    params["X-Plex-Token"] = PLEX_TOKEN

    headers = {"Accept": "application/json"}
    url = f"{PLEX_URL}{endpoint}"

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


@app.route("/")
def index():
    """Serve the main UI."""
    return render_template("index.html")


@app.route("/api/sections")
def get_sections():
    """List all library sections."""
    try:
        data = plex_request("/library/sections")
        sections = []
        for section in data.get("MediaContainer", {}).get("Directory", []):
            sections.append({
                "id": section["key"],
                "title": section["title"],
                "type": section["type"],
            })
        return jsonify(sections)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sections/<section_id>")
def get_section_items(section_id):
    """Get items in a library section."""
    try:
        data = plex_request(f"/library/sections/{section_id}/all")
        container = data.get("MediaContainer", {})
        items = []

        for item in container.get("Metadata", []):
            item_data = {
                "id": item["ratingKey"],
                "title": item["title"],
                "type": item["type"],
            }
            # Include the file path for movies or the show path for TV
            if "Media" in item and item["Media"]:
                parts = item["Media"][0].get("Part", [])
                if parts:
                    item_data["path"] = parts[0].get("file", "")
            elif "Location" in item:
                # For TV shows, get the location path
                item_data["path"] = item["Location"][0].get("path", "")

            items.append(item_data)

        return jsonify({
            "title": container.get("title1", ""),
            "items": items,
            "section_id": section_id,
        })
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/shows/<show_id>/seasons")
def get_seasons(show_id):
    """Get seasons for a TV show."""
    try:
        data = plex_request(f"/library/metadata/{show_id}/children")
        container = data.get("MediaContainer", {})
        seasons = []

        for season in container.get("Metadata", []):
            seasons.append({
                "id": season["ratingKey"],
                "title": season["title"],
                "index": season.get("index", 0),
            })

        return jsonify({
            "title": container.get("parentTitle", ""),
            "seasons": seasons,
            "show_id": show_id,
        })
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/seasons/<season_id>/episodes")
def get_episodes(season_id):
    """Get episodes in a season."""
    try:
        data = plex_request(f"/library/metadata/{season_id}/children")
        container = data.get("MediaContainer", {})
        episodes = []

        for episode in container.get("Metadata", []):
            ep_data = {
                "id": episode["ratingKey"],
                "title": episode["title"],
                "index": episode.get("index", 0),
            }
            if "Media" in episode and episode["Media"]:
                parts = episode["Media"][0].get("Part", [])
                if parts:
                    ep_data["path"] = parts[0].get("file", "")
            episodes.append(ep_data)

        return jsonify({
            "show_title": container.get("grandparentTitle", ""),
            "season_title": container.get("parentTitle", ""),
            "episodes": episodes,
            "season_id": season_id,
        })
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/refresh", methods=["POST"])
def refresh():
    """Trigger a library refresh."""
    try:
        data = request.get_json()
        section_id = data.get("section_id")
        path = data.get("path")

        if not section_id:
            return jsonify({"error": "section_id is required"}), 400

        params = {"X-Plex-Token": PLEX_TOKEN}
        if path:
            params["path"] = path

        url = f"{PLEX_URL}/library/sections/{section_id}/refresh"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        return jsonify({"success": True, "message": "Refresh triggered successfully"})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # Re-read after loading .env
    PLEX_URL = os.environ.get("PLEX_URL", "").rstrip("/")
    PLEX_TOKEN = os.environ.get("PLEX_TOKEN", "")

    if not PLEX_URL or not PLEX_TOKEN:
        print("Error: PLEX_URL and PLEX_TOKEN environment variables are required")
        exit(1)

    app.run(debug=True, host="0.0.0.0", port=5000)
