from flask import Blueprint, render_template, request, redirect, url_for, session
from config.spotify import sp
from utils import get_playlist_tracks, create_playlist, add_tracks_to_playlist

choose_playlists_profil = Blueprint("choose_playlists_profil", __name__)

@choose_playlists_profil.route("/choose/profile/playlists", methods=["GET", "POST"])
def index():
    playlists = sp.current_user_playlists()["items"]  # Récupère toutes les playlists

    return render_template("choose_playlists_profil.html", playlists=playlists)


@choose_playlists_profil.route("/process_playlists", methods=["POST"])
def process_playlists():
    """Gère les actions après la sélection des playlists"""
    playlist_ids = request.form.getlist("playlist_ids")
    playlist_name = request.form.get("playlist_name")  # ✅ Récupérer le nom entré par l'utilisateur
    operation = request.form.get("operation")

    if not playlist_ids:
        return "❌ Vous devez sélectionner au moins une playlist.", 400

    if operation == "intersect" and not playlist_name:
        return "❌ Vous devez entrer un nom pour la nouvelle playlist.", 400

    # Stocker la sélection dans une session pour pouvoir l'utiliser après redirection
    session["selected_playlists"] = playlist_ids
    session["playlist_name"] = playlist_name if operation == "intersect" else None
    session["operation"] = operation

    if operation == "intersect":
        return redirect(url_for("choose_playlists_profil.create_intersection_playlist"))
    elif operation == "delete":
        return redirect(url_for("choose_playlists_profil.delete_playlists"))

    return "❌ Opération inconnue.", 400

@choose_playlists_profil.route("/create_intersection_playlist", methods=["GET"])
def create_intersection_playlist():
    """Crée une playlist contenant uniquement les musiques présentes dans toutes les playlists sélectionnées"""
    selected_playlists = session.get("selected_playlists", [])
    playlist_name = session.get("playlist_name", "Playlist Intersect 🎶")  # ✅ Utiliser le nom donné par l'utilisateur

    if not selected_playlists:
        return "❌ Aucune playlist sélectionnée.", 400

    user_id = sp.me()["id"]

    # Récupérer les morceaux de chaque playlist sélectionnée
    track_sets = []
    for playlist_id in selected_playlists:
        tracks = get_playlist_tracks(sp, playlist_id)
        track_sets.append(set(track["id"] for track in tracks))

    # Trouver l'intersection des morceaux
    common_tracks = set.intersection(*track_sets) if track_sets else set()

    if not common_tracks:
        return "❌ Aucun morceau commun trouvé entre les playlists sélectionnées.", 400

    # Créer une nouvelle playlist avec le nom personnalisé
    new_playlist_id = create_playlist(sp, user_id, playlist_name)

    # Ajouter les morceaux communs à la playlist
    add_tracks_to_playlist(sp, new_playlist_id, list(common_tracks))

    return redirect(url_for("choose_playlists_profil.index"))

@choose_playlists_profil.route("/delete_playlists", methods=["GET"])
def delete_playlists():
    """Supprime les playlists sélectionnées"""
    selected_playlists = session.get("selected_playlists", [])

    if not selected_playlists:
        return "❌ Aucune playlist sélectionnée.", 400

    for playlist_id in selected_playlists:
        try:
            sp.user_playlist_unfollow(sp.me()["id"], playlist_id)  # Supprime la playlist
            print(f"🗑️ Playlist supprimée : {playlist_id}")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de la playlist {playlist_id} : {e}")

    return redirect(url_for("choose_playlists_profil.index"))