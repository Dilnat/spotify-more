import spotipy
from spotipy.oauth2 import SpotifyOAuth
from utils import get_user_id
from utils import get_playlist_tracks
from utils import choose_playlists
from utils import create_playlist
from utils import add_tracks_to_playlist

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="6a8089e3d69845698721456dee2341ec",
                                               client_secret="c697209a5c884f17a64a7abc82c753c1",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="playlist-read-private playlist-modify-private playlist-modify-public"))

playlists = sp.current_user_playlists()

playlist_tracks_list = [get_playlist_tracks(sp, pid) for pid in choose_playlists(playlists)]
if playlist_tracks_list:
    common_tracks = set.intersection(*playlist_tracks_list)
else:
    common_tracks = set()


print("\n🎵 **Musiques présentes dans toutes les playlists sélectionnées :**\n")
if common_tracks:
    for idx, (track_name, artist_name, track_id) in enumerate(common_tracks, start=1):
        print(f"{idx}. {track_name} - {artist_name} - {track_id}")

    # 📌 Demander le nom de la nouvelle playlist
    new_playlist_name = input("\n🎼 Nom de la nouvelle playlist à créer : ")

    # 📌 Récupérer l'ID utilisateur
    user_id = get_user_id(sp)

    # 📌 Créer une nouvelle playlist
    new_playlist_id = create_playlist(sp, user_id, new_playlist_name)
    print(f"\n✅ Playlist '{new_playlist_name}' créée avec succès !")

    # 📌 Ajouter les morceaux à la nouvelle playlist
    track_ids = [track[2] for track in common_tracks]  # Extraire seulement les track IDs
    add_tracks_to_playlist(sp, new_playlist_id, track_ids)

    print(f"\n✅ {len(track_ids)} musiques ajoutées à '{new_playlist_name}' 🎶")
else:
    print("🚫 Aucune musique en commun entre ces playlists.")