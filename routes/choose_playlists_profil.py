from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from config.spotify import sp
from utils import get_playlist_tracks, create_playlist, add_tracks_to_playlist, display_playlists_ids_terminal, get_tracks_from_playlists

choose_playlists_profil = Blueprint("choose_playlists_profil", __name__)

@choose_playlists_profil.route("/choose/profile/playlists", methods=["GET", "POST"])
def index():
    playlists = sp.current_user_playlists()["items"]  # Récupère toutes les playlists

    return render_template("choose_playlists_profil.html", playlists=playlists, enumerate=enumerate)

@choose_playlists_profil.route("/save_selected_playlists", methods=["POST"])
def save_selected_playlists():
    """Stocke les playlists sélectionnées dans la session Flask"""

    try:
        data = request.get_json()
        print("📌 Données reçues :", data)  # ✅ Debug : voir les données envoyées par JS

        # ✅ Stocker en session Flask
        session["selected_playlists"] = data["playlists"]
        print(f"✅ Playlists enregistrées en session : {session['selected_playlists']}")

        return jsonify({"message": "✅ Playlists sélectionnées avec succès !"}), 200
    
    except Exception as e:
        print(f"❌ Erreur côté serveur : {e}")
        return jsonify({"error": "Erreur serveur"}), 500


@choose_playlists_profil.route("/process_playlists", methods=["POST"])
def process_playlists():
    """Gère les actions après la sélection des playlists"""
    playlist_name = request.form.get("playlist_name")  # ✅ Récupérer le nom entré par l'utilisateur
    operation = request.form.get("operation")

    if (operation == "intersect" or operation == "minus") and not playlist_name:
        return "❌ Vous devez entrer un nom pour la nouvelle playlist.", 400

    # Stocker la sélection dans une session pour pouvoir l'utiliser après redirection
    session["playlist_name"] = playlist_name if operation == "intersect" or operation == "minus" else None
    session["operation"] = operation
    
    if operation == "intersect":
        return redirect(url_for("choose_playlists_profil.create_intersection_playlist"))
    elif operation == "delete":
        return redirect(url_for("choose_playlists_profil.delete_playlists"))
    elif operation == "minus":
        return redirect(url_for("choose_playlists_profil.create_minus_playlist"))

    return "❌ Opération inconnue.", 400

@choose_playlists_profil.route("/select_playlists", methods=["GET", "POST"])
def select_playlists():
    """Affiche les playlists et permet à l'utilisateur de les choisir dans un ordre spécifique"""
    playlists = sp.current_user_playlists()

    if request.method == "POST":
        user_input = request.form.get("selected_playlists")  # Exemple : "3,1,2"
        playlist_indexes = [i.strip() for i in user_input.split(",") if i.strip().isdigit()]

        if not playlist_indexes:
            return "❌ Aucune playlist valide sélectionnée.", 400

        selected_playlists = [playlists["items"][int(i) - 1]["id"] for i in playlist_indexes if int(i) - 1 < len(playlists["items"])]

        if len(selected_playlists) < 2:
            return "❌ Vous devez sélectionner au moins deux playlists.", 400

        # ✅ Stocker les playlists sélectionnées dans l'ordre choisi
        session["selected_playlists"] = selected_playlists
        return redirect(url_for("choose_playlists_profil.index"))

    return render_template("choose_playlists.html", playlists=playlists, enumerate=enumerate)



# Intersection des playlists
@choose_playlists_profil.route("/create_intersection_playlist", methods=["GET"])
def create_intersection_playlist():
    """Crée une playlist contenant uniquement les musiques présentes dans toutes les playlists sélectionnées"""
    selected_playlists = session.get("selected_playlists", [])
    playlist_name = session.get("playlist_name", "Playlist Intersect 🎶")  # ✅ Utiliser le nom donné par l'utilisateur

    if not selected_playlists:
        return "❌ Aucune playlist sélectionnée.", 400


    user_id = sp.me()["id"]

    # Récupérer les morceaux de chaque playlist sélectionnée
    track_sets = get_tracks_from_playlists(sp, playlists=selected_playlists)

    # Trouver l'intersection des morceaux
    common_tracks = set.intersection(*track_sets) if track_sets else set()

    if not common_tracks:
        return "❌ Aucun morceau commun trouvé entre les playlists sélectionnées.", 400

    # Créer une nouvelle playlist avec le nom personnalisé
    new_playlist_id = create_playlist(sp, user_id, playlist_name)

    # Ajouter les morceaux communs à la playlist
    add_tracks_to_playlist(sp, new_playlist_id, list(common_tracks))

    return redirect(url_for("choose_playlists_profil.index"))


# Minus 
@choose_playlists_profil.route("/create_minus_playlist", methods=["GET"])
def create_minus_playlist():
    """Crée une nouvelle playlist contenant toutes les musiques de la première playlist moins les musiques présentent dans les autres playlists"""
    """Minimum deux playlists requises"""
    selected_playlists = session.get("selected_playlists", [])
    playlist_name = session.get("playlist_name", "Playlist Minus 🎵")  # Nom personnalisé de la nouvelle playlist

    if len(selected_playlists) < 2:
        return "❌ Au moins deux playlists doivent être sélectionnées.", 400

    user_id = sp.me()["id"]

    # 🎵 Récupérer les morceaux de chaque playlist sélectionnée
    track_sets = get_tracks_from_playlists(sp, playlists=selected_playlists)

    # 🏆 Déterminer les morceaux à conserver (ceux uniquement dans la première playlist)
    first_playlist_tracks = track_sets[0]  # 🎯 Playlist principale
    other_playlists_tracks = set.union(*track_sets[1:])  # 🔥 Toutes les autres playlists combinées

    # 🛑 Supprimer de `first_playlist_tracks` les musiques présentes dans `other_playlists_tracks`
    unique_tracks = first_playlist_tracks - other_playlists_tracks

    if not unique_tracks:
        return "❌ Aucun morceau unique trouvé dans la première playlist.", 400

    # 🎼 Créer une nouvelle playlist
    new_playlist_id = create_playlist(sp, user_id, playlist_name)

    # ➕ Ajouter les morceaux restants à la nouvelle playlist
    add_tracks_to_playlist(sp, new_playlist_id, list(unique_tracks))

    return redirect(url_for("choose_playlists_profil.index"))



# Suppression des playlists
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