import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import jsonify
def get_user_id(sp):
    """Récupère l'ID de l'utilisateur Spotify."""
    user_info = sp.me()
    return user_info["id"]

def create_playlist(sp, user_id, playlist_name):
    """Crée une nouvelle playlist et retourne son ID"""
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)  # Playlist privée par défaut
    return playlist["id"]

def add_tracks_to_playlist(sp, playlist_id, track_ids):
    """Ajoute les musiques dans la playlist par lots de 100 pour éviter l'erreur"""
    track_ids = [tid for tid in track_ids if tid is not None]  # Filtrer les morceaux valides
    
    if not track_ids:
        print("🚫 Aucun morceau valide à ajouter.")
        return
    
    chunk_size = 100  # Spotify limite à 100 morceaux par requête
    
    for i in range(0, len(track_ids), chunk_size):
        batch = track_ids[i:i + chunk_size]  # Découpe en paquets de 100
        sp.playlist_add_items(playlist_id, batch)
        print(f"✅ {len(batch)} morceaux ajoutés...")

    print(f"\n✅ {len(track_ids)} musiques ajoutées à la playlist ! 🎶")

def get_playlist_tracks(sp, playlist_id):
    """Récupère toutes les musiques d'une playlist, même si elle dépasse 100 morceaux"""
    tracks = []
    offset = 0
    limit = 100  # Maximum autorisé par Spotify

    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)

        if not results or "items" not in results:  # Vérifie si la réponse est valide
            print("⚠️ Erreur : Impossible de récupérer les morceaux de la playlist.")
            break

        items = results["items"]
        if not items:  # Si plus de morceaux à récupérer, on arrête
            break

        for item in items:
            track = item.get("track")  # Sécurisé avec `.get()` pour éviter KeyError
            if track:
                track_name = track.get("name", "Inconnu")
                artist_name = track["artists"][0]["name"] if track.get("artists") else "Artiste inconnu"
                track_id = track.get("id")  # Récupérer l'ID du morceau pour pouvoir l'ajouter plus tard
                duration_ms = track.get("duration_ms", 0)  # ✅ Récupération correcte de la durée

                if track_id:  # Vérifie si le morceau a bien un ID Spotify
                    tracks.append({
                        "name": track_name,
                        "artist": artist_name,
                        "id": track_id,
                        "duration_ms": duration_ms
                    })
                else:
                    print(f"⚠️ Musique locale ignorée : {track_name} - {artist_name}")

        offset += limit  # On avance de 100 morceaux pour la prochaine requête

    return tracks

def choose_playlists(playlists):
    playlist_dict = {}  # Dictionnaire pour stocker les noms et IDs des playlists

    print("\n📜 **Liste de tes playlists Spotify :**\n")
    for idx, playlist in enumerate(playlists["items"], start=1):
        name = playlist["name"]
        playlist_id = playlist["id"]
        print(f"{idx}. {name} - ID: {playlist_id}")
        playlist_dict[str(idx)] = playlist_id  # Associer un numéro à chaque playlist

    # 📌 Demander à l'utilisateur de choisir plusieurs playlists
    selected_playlists = []
    while True:
        user_input = input("\n🎵 Saisis les numéros ou IDs des playlists (séparés par des virgules) : ")
        user_choices = [choice.strip() for choice in user_input.split(",")]

        for choice in user_choices:
            if choice in playlist_dict:  # Si c'est un numéro
                selected_playlists.append(playlist_dict[choice])
            elif choice in [p["id"] for p in playlists["items"]]:  # Si c'est un ID valide
                selected_playlists.append(choice)
            else:
                print(f"❌ Entrée invalide : {choice} (ignoring)")

        if selected_playlists:
            break
        else:
            print("⚠️ Aucune playlist valide sélectionnée, réessaye.")
    return selected_playlists

def get_user_playlists(sp):
    try:
        playlists = sp.current_user_playlists()
        playlists_data = []

        for playlist in playlists["items"]:
            playlist_id = playlist["id"]
            playlist_tracks = get_playlist_tracks(sp, playlist_id)

            # Calcul de la durée totale en millisecondes
            total_duration_ms = sum(track["duration_ms"] for track in playlist_tracks if "duration_ms" in track)

            playlists_data.append({
                "name": playlist["name"],
                "id": playlist["id"],
                "tracks":  len(playlist_tracks),
                "duration": format_duration(total_duration_ms),
                "image_url": playlist["images"][0]["url"] if playlist["images"] else None,
                "owner": playlist["owner"]["display_name"]
            })

        return playlists_data
    
    except Exception as e:
        print(f"❌ Erreur lors du traitement de la playlist : {e}")

def get_user_playlists_name(sp):
    try:
        return sp.current_user_playlists()
    except Exception as e:
        print(f"❌ Erreur lors du traitement des playlists : {e}")

def format_duration(ms):
    """Convertit la durée en millisecondes en heures, minutes et secondes"""
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60

    if hours > 0:
        return f"{hours} h {minutes % 60} min {seconds % 60} sec"
    else:
        return f"{minutes} min {seconds % 60} sec"
    
def display_playlists_terminal(playlists):
    """Affiche une liste de playlists Spotify dans le terminal."""
    
    if not playlists or "items" not in playlists:
        print("🚫 Aucune playlist trouvée.")
        return
    
    print("\n🎵 **Liste des playlists Spotify :**\n")
    print("=" * 60)

    for idx, playlist in enumerate(playlists["items"], start=1):
        name = playlist["name"]
        track_count = playlist["tracks"]["total"]
        playlist_url = playlist["external_urls"]["spotify"]

        print(f"{idx:>2}. 📂 {name}")
        print(f"    🔢 Nombre de morceaux : {track_count}")
        print(f"    🔗 Lien : {playlist_url}")
        print("=" * 60)
    
    print("\n✅ **Affichage terminé !**")

def display_playlists_ids_terminal(playlists_ids):
    """Affiche une liste des id des playlists Spotify dans le terminal."""
    
    if not playlists_ids:
        print("🚫 Aucune playlist trouvée.")
        return
    
    print("\n🎵 **Liste des id des playlists Spotify :**\n")
    print("=" * 60)

    for idx, id in enumerate(playlists_ids, start=1):
        print(f"{idx} : 📂 {id}")
    
    print("\n✅ **Affichage terminé !**")


def display_playlists_names_terminal(playlists_names):
    """Affiche une liste des id des playlists Spotify dans le terminal."""
    
    if not playlists_names:
        print("🚫 Aucune playlist trouvée.")
        return
    
    print("\n🎵 **Liste des noms des playlists Spotify :**\n")
    print("=" * 60)

    for idx, name in enumerate(playlists_names, start=1):
        print(f"{idx} : 📂 {name}")
    
    print("\n✅ **Affichage terminé !**")



def get_tracks_from_playlists(sp, playlists):
    track_sets = []
    for playlist_id in playlists:
        tracks = get_playlist_tracks(sp, playlist_id)
        track_sets.append(set(track["id"] for track in tracks))
    return track_sets

def get_track_features(sp, track_id):
    try:
        features = sp.audio_features(track_id)
        if features and features[0]:  # Check if features exist
            return {
                "danceability": features[0]["danceability"],
                "energy": features[0]["energy"],
                "valence": features[0]["valence"],
                "tempo": features[0]["tempo"],
                "acousticness": features[0]["acousticness"],
                "instrumentalness": features[0]["instrumentalness"],
                "loudness": features[0]["loudness"]
            }
        else:
            print(f"Warning: No audio features found for track {track_id}")
            return None
    except Exception as e:
        print("Error fetching track features:", e)
        return None