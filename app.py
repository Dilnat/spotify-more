from flask import Flask
from routes.search_track import search_track
from routes.search_playlists_profil import search_playlists_profil
from routes.choose_playlists_profil import choose_playlists_profil
from routes.home import home;
from routes.profil import profil;
from config.spotify import sp 
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

def get_track_image(track_id):
    """Récupère l'image d'un morceau (pochette d'album)"""
    track = sp.track(track_id)
    image_url = track["album"]["images"][0]["url"]  # Première image (haute qualité)

    print(f"🎵 Titre : {track['name']}")
    print(f"📀 Album : {track['album']['name']}")
    print(f"🖼️ Pochette : {image_url}")
    return image_url

app.register_blueprint(search_track)
app.register_blueprint(search_playlists_profil)
app.register_blueprint(choose_playlists_profil)
app.register_blueprint(home)
app.register_blueprint(profil)

# @app.route("/intersection", methods=["GET", "POST"])
# def intersection():
#     return render_template("intersection.html", playlists=playlists)

if __name__ == "__main__":
    app.run(debug=True)
