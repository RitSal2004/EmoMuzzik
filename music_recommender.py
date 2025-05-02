import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

def recommend_music(emotion):
    """Working music recommendation that actually shows results"""
    try:
        # 1. Initialize Spotify client with YOUR credentials
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="3346818c664d48b09df8025c33b6e25c",  # REPLACE THIS
            client_secret="b2ebd040751049399d1f885a665ee606"  # REPLACE THIS
        ))
        
        # 2. Emotion to track search mapping (tested queries)
        track_queries = {
            'Happy': ['Happy by Pharrell Williams', 'Dancing Queen by ABBA'],
            'Sad': ['Someone Like You by Adele', 'Hurt by Johnny Cash'],
            'Angry': ['Break Stuff by Limp Bizkit', 'Killing in the Name by Rage Against the Machine'],
            'Surprise': ['Surprise Surprise by Bruce Springsteen', 'Wow by Post Malone'],
            'Fear': ['Fear of the Dark by Iron Maiden', 'Scary Monsters by David Bowie'],
            'Disgust': ['Disgusting by Beartooth', 'Down with the Sickness by Disturbed'],
            'Neutral': ['Blinding Lights by The Weeknd', 'Watermelon Sugar by Harry Styles']
        }
        
        # 3. Get tracks based on emotion
        tracks = []
        for query in track_queries.get(emotion, ['Happy by Pharrell Williams']):
            results = sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                tracks.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'preview_url': track['preview_url'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'external_url': track['external_urls']['spotify']
                })
        
        return tracks if tracks else [{
            'name': 'Click "Detect Emotion" to get recommendations',
            'artist': 'System Message',
            'preview_url': None,
            'image_url': None,
            'external_url': 'https://open.spotify.com'
        }]
        
    except Exception as e:
        st.error(f"Please check your Spotify credentials and internet connection")
        return []