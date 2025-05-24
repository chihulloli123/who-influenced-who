from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

app = Flask(__name__)

# Spotify client auth
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

# Recursive related artists tree builder
def build_tree(artist_id, depth=0, max_depth=2):
    if depth >= max_depth:
        return []
    related = sp.artist_related_artists(artist_id)["artists"]
    children = []
    for artist in related[:3]:  # limit to 3 branches per node
        child = {
            "name": artist["name"],
            "id": artist["id"],
            "children": build_tree(artist["id"], depth + 1, max_depth)
        }
        children.append(child)
    return children

# API route to get influence tree
@app.route("/tree", methods=["GET"])
def get_tree():
    name = request.args.get("artist")
    if not name:
        return jsonify({"error": "No artist specified"}), 400

    results = sp.search(q=name, type="artist", limit=1)
    items = results["artists"]["items"]
    if not items:
        return jsonify({"error": "Artist not found"}), 404

    root = items[0]
    tree = {
        "name": root["name"],
        "id": root["id"],
        "children": build_tree(root["id"])
    }
    return jsonify(tree)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
