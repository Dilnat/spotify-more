from flask import Blueprint, render_template, request
from config.spotify import sp

home = Blueprint("home", __name__)

@home.route("/", methods=["GET"])
def index():
    user = sp.me()
    user_info = {
        "display_name": user["display_name"],
        "id": user["id"],
        "followers": user["followers"]["total"],
        "profile_url": user["external_urls"]["spotify"],
        "image_url": user["images"][0]["url"] if user["images"] else None
    }
    return render_template("home.html", user_info=user_info)
