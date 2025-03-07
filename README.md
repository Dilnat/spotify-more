# How to use it

clone the project, go into the repository that it create and run the following command : 

## Create a virtual environment
```bash
python3 -m venv venv
```

## Activate the virtual environment :  
```bash
source venv/bin/activate
```
If you want to desactivate : 
```bash
deactivate
```

## Install dependencies : 
```bash
pip install -r requirements.txt
```

Verify Flask installation : 
```bash
flask --version 
```

# Configuration

Go to "Spotify for developers" : https://developer.spotify.com/ 

Connect to your spotify account and create an application 

Once you're in the dashboard of your application go to settings

In Basic information, get your client id and client secret (do NOT share it with anyone !)

## Create an environment file : 
```bash
touch .env
```

Add the following lines in the file and replace the <> by client id and client secret : 
```
SPOTIPY_CLIENT_ID=<>
SPOTIPY_CLIENT_SECRET=<>
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
SPOTIPY_SCOPE=ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-follow-modify user-follow-read user-read-playback-position user-top-read user-read-recently-played user-library-modify user-library-read user-read-email user-read-private user-soa-link user-soa-unlink soa-manage-entitlements soa-manage-partner soa-create-partner
```

# Run the application 
```bash
python3 app.py
```