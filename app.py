from flask import Flask, request, render_template
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# Flask
app = Flask(__name__)
# Set up credentials

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='74f3dd6a119c4711b8e141ff02303dde',
    client_secret='36dc856cff2d46b3a3a920f6a80665c5',
    redirect_uri='http://www.localhost/'))
try:
    sp.current_user()
except spotipy.SpotifyException as e:
    print(f"Error: {e}")
else:
    print("Token is valid.")

token = sp.auth_manager.get_cached_token()
# print(token_data['access_token'])
# Set up headers with authorization token
headers = {
    'Authorization': 'Bearer ' + token['access_token']
}
# Define route for index page
@app.route('/')
def index():
    print('Hola')
    return render_template('index.html')
# Define route for recommendations page
def get_seed(seed_name, seed_chosen):
    if (seed_name == "Artist"):
        # Search for an artist
        results = sp.search(q=seed_chosen, type='artist')
        items = results['artists']['items']
        if len(items) > 0:
            # Get the Spotify ID of the first artist in the results
            artist_id = items[0]['id']
            return {'seed_artists': artist_id}
        else:
            print("No artist found")
            return None

    else:
        results = sp.search(q=seed_chosen, type='track', limit=1)
        if len(results['tracks']['items']) > 0:
            track_id = results['tracks']['items'][0]['id']
            return {'seed_tracks': track_id}
        else:
            return None

@app.route('/recommendations', methods=['POST'])
def recommendations():
    print('jeje')
    # Set up query parameters

    seed_name = request.form['seed']
    seed_chosen = request.form['seedChosen']
    seed = get_seed(seed_name, seed_chosen)
    
    print(seed)
    
    market = request.form['market']
    genre = request.form['genre']
    danceability = request.form['danceability']
    acousticness = request.form['acousticness']
    popularity = request.form['popularity']
    

    query_params = {
        'market' : market,
        'seed_genres': genre,
        **seed,
        'target_danceability': danceability,
        'target_acousticness': acousticness,
        'target_popularity': popularity,
        'limit': 10
    }

    # Make API request to get recommendations
    response = requests.get('https://api.spotify.com/v1/recommendations', headers=headers, params=query_params)

    # Parse response JSON
    response_json = response.json()


    # Get list of recommended tracks
    tracks = response_json['tracks']

    # Print track names and artists
    #for track in tracks:
    #    print(track['name'], 'by', track['artists'][0]['name'])
    iframe_list = []
    for track in tracks:
        track_id = track['id']
        embed_url = f"https://open.spotify.com/embed/track/{track_id}"
        iframe = f'<iframe src="{embed_url}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
        iframe_list.append(iframe)

    return render_template('index.html', iframe_list=iframe_list)
if __name__ == '__main__':
    app.run(debug=False, port=80)

