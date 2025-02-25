from flask import Blueprint, render_template, request
from config.spotify import sp
from utils import get_user_playlists
search_playlists_profil = Blueprint("search_playlists_profil", __name__)

@search_playlists_profil.route("/search/profile/playlists", methods=["GET", "POST"])
def index():
    playlists = get_user_playlists(sp)
    print(playlists)
    playlist_info = None
    error = None
    if request.method == "POST":
        playlist_name = request.form["playlist_name"].strip()
        matching_playlists = [p for p in playlists if p["name"].lower() == playlist_name.lower()]

        if matching_playlists:
            playlist_info = matching_playlists[0]  # Prend la première correspondance
        else:
            error = "❌ Aucune playlist trouvée avec ce nom."

    return render_template("search_playlists_profil.html", playlist_info=playlist_info, error=error, playlists=playlists)
