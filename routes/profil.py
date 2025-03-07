from flask import Blueprint, render_template, request, redirect, url_for, session
from config.spotify import sp

profil = Blueprint("profil", __name__)

@profil.route("/profil", methods=["GET"])
def index():
    user = sp.me()
    user_info = {
        "display_name": user["display_name"],
        "id": user["id"],
        "followers": user["followers"]["total"],
        "profile_url": user["external_urls"]["spotify"],
        "image_url": user["images"][0]["url"] if user["images"] else None
    }

    session["user_info"] = user_info

    return render_template("profil.html", user_info=user_info)

@profil.route("/profil/tracks", methods=["GET", "POST"])
def update_top_tracks():
    number_tracks = request.form.get("number_tracks", 10).strip()  # Valeur par défaut = 10
    if not number_tracks.isdigit():
        number_tracks = 10
    else:
        number_tracks = int(number_tracks)
    time_range = request.form.get("time_range", "medium_term")  # Valeur par défaut = 6 mois

    session["number_tracks"] = number_tracks
    session["time_range"] = time_range

    # 📌 Récupérer `user_info` depuis `session`
    user_info = session.get("user_info")

    # 🎵 Récupérer les morceaux les plus écoutés avec les nouvelles valeurs
    top_tracks = sp.current_user_top_tracks(limit=int(number_tracks), time_range=time_range)

    # ✅ Extraire les infos des morceaux
    top_tracks_list = []
    for track in top_tracks["items"]:
        top_tracks_list.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "image_url": track["album"]["images"][0]["url"],
            "preview_url": track["preview_url"],
            "spotify_url": track["external_urls"]["spotify"]
        })
    user_info = session.get("user_info")
    return render_template(
        "profil.html", 
        user_info=user_info, 
        top_tracks=top_tracks_list, 
        selected_number_tracks=number_tracks,
        selected_time_range=time_range)
