# Testing out Spotify API
 
import os
from dotenv import load_dotenv
import requests
import urllib.parse
from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify, session


load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = 'http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1'

app = Flask(__name__)
app.secret_key = 'tyWD8I13zSQAWHY2z2xP9wc80j4JJ7Ov'

@app.route('/')
def index():
    return "Hey Sisters <a href='/login'>Login here</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        'show_dialog': True
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    print(request.args)
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_data = {
            "code": request.args['code'],
            "grant_type": 'authorization_code',
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret
        }
    
        response = requests.post(TOKEN_URL, data=req_data)
        token_info = response.json()
        print(token_info)
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlists')
    
@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print('token bad, must refresh :()')
        return redirect('/refresh-token')
    
    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()
    print(playlists)
    return jsonify(playlists)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_data = {
            "grant_type": 'refresh_token',
            "refresh_token": session['refesh_token'],
            "client_id": client_id,
            "client_secret": client_secret
        }

        response = requests.post(TOKEN_URL, data=req_data)
        new_token_info = response.json()
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
        return redirect('/playlists')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
