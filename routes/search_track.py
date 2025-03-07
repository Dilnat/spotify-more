from flask import Blueprint, render_template, request
from config.spotify import sp, sp_oauth
from utils import get_track_features
import pandas as pd
search_track = Blueprint("search_track", __name__)


@search_track.route("/search/track", methods=["GET", "POST"])
def index():
    track_info = None
    error = None
    track_id = "3n3Ppam7vgaVa1iaRUc9Lp"  # Example: Stairway to Heaven

    try:
        features = sp_oauth.audio_features(track_id)
        print(features)
    except Exception as e:
        print(f"Error fetching track features: {e}")
    if request.method == "POST":
        track_name = request.form["track_name"].strip()

        try:
            results = sp.search(q=track_name, type="track", limit=1)
            print(results)
            if results["tracks"]["items"]:
                track = results["tracks"]["items"][0]  # Premier (meilleur) résultat
                track_info = {
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"],
                    "release_date": track["album"]["release_date"],
                    "duration": f"{track['duration_ms'] // 60000} min {track['duration_ms'] // 1000 % 60} sec",
                    "explicit": "🔞 Oui" if track["explicit"] else "✅ Non",
                    "popularity": f"{track['popularity']}/100",
                    "image_url": track["album"]["images"][0]["url"],
                    "preview_url": track["preview_url"],
                    "id": track["id"]
                }
            else:
                error = "❌ Aucun résultat trouvé pour ce titre."
        except Exception as e:
            error = "❌ Impossible de récupérer les informations. Vérifie le nom du morceau."

    return render_template("search_track.html", track_info=track_info, error=error)


