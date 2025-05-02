import streamlit as st
import requests
from PIL import Image, ImageOps
import numpy as np
import io
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Emotion labels
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

# Predefined playlist URLs for Happy Emotion
happy_playlists = [
    "https://open.spotify.com/playlist/2gSHA2hK9utrPK6ldtJgws",
    "https://open.spotify.com/playlist/1fF73hY1QzokhWz5RTeoRb",
    "https://open.spotify.com/playlist/4F9XjRMCeyxlmysK16V85W"
]

# Spotify-friendly emotion-to-query mapping
emotion_queries = {
    "sad": ["sad songs", "melancholy vibes", "emotional music"],
    "angry": ["workout music"],
    "fear": ["dark cinematic", "suspense music"],
    "surprise": ["unexpected hits", "eclectic mix"],
    "disgust": ["grunge punk", "heavy metal"],
    "neutral": ["calm lofi", "study music"]
}

# Spotify API setup
client_id = "3346818c664d48b09df8025c33b6e25c"
client_secret = "b2ebd040751049399d1f885a665ee606"
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def search_spotify_playlists(query_list, limit=3):
    playlists = []
    for query in query_list:
        try:
            results = sp.search(q=query, type='playlist', limit=limit)
            items = results.get('playlists', {}).get('items', [])
            for item in items:
                if 'external_urls' in item:
                    playlists.append(item['external_urls']['spotify'])
            if len(playlists) >= limit:
                break
        except Exception as e:
            st.error(f"🔍 Spotify Search Error: {e}")
    return playlists

# REST API URL (change this to your deployed API endpoint)
API_URL = "https://your-api-url.onrender.com/predict"

def get_emotion_from_api(image: Image.Image):
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        buffered.seek(0)
        files = {'file': ('image.jpg', buffered, 'image/jpeg')}
        response = requests.post(API_URL, files=files, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("emotion", "neutral")
    except Exception as e:
        st.warning("⚠️ Could not detect emotion. Defaulting to neutral.")
        return "neutral"

# Streamlit UI
st.set_page_config(page_title="EmoMuzzik", page_icon="🎧")
st.title("🎭 Welcome to EmoMuzzik")
st.subheader("🎶 Your Emotion-Based Spotify Music Companion")

# Session state
for key in ["camera_active", "favorites", "override_emotion", "emotion_changed"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "favorites" else False

col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start Camera"):
        st.session_state.camera_active = True
with col2:
    if st.button("⏹️ Stop Camera"):
        st.session_state.camera_active = False

# Favorites section
with st.expander("⭐ View My Favorite Tracks"):
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.markdown(f"[Open Playlist]({fav})")
            st.components.v1.iframe(fav.replace("open.spotify.com", "open.spotify.com/embed"), height=80)
    else:
        st.info("No favorites yet — like a playlist to save it here!")

if st.session_state.camera_active:
    img_file = st.camera_input("📸 Capture a photo")

    if img_file:
        img = Image.open(img_file)
        mirrored_img = ImageOps.mirror(img)
        st.image(mirrored_img, use_container_width=True)

        st.info("⏳ Sending image to emotion detection API...")
        detected_emotion = get_emotion_from_api(mirrored_img)

        st.session_state.override_emotion = st.selectbox(
            "Change Emotion (if incorrect):",
            options=emotion_labels,
            index=emotion_labels.index(detected_emotion)
        )

        st.session_state.emotion_changed = (st.session_state.override_emotion != detected_emotion)
        emotion = st.session_state.override_emotion

        st.subheader(f"🎯 Final Emotion Selected: **{emotion.capitalize()}**")
        if st.session_state.emotion_changed:
            st.caption("🙇 Sorry if we detected the wrong emotion — we're still improving!")

        st.success(f"🎶 Recommended Playlists for **{emotion.capitalize()}**:")
        if emotion == "happy":
            for link in happy_playlists:
                st.markdown(f"[Open Playlist]({link})")
                st.components.v1.iframe(link.replace("open.spotify.com", "open.spotify.com/embed"), height=80)
        elif emotion in emotion_queries:
            queries = emotion_queries[emotion]
            playlists = search_spotify_playlists(queries)
            for link in playlists:
                st.markdown(f"[Open Playlist]({link})")
                st.components.v1.iframe(link.replace("open.spotify.com", "open.spotify.com/embed"), height=80)

        with st.expander("❤️ Did you like the recommendation?"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Like"):
                    all_links = happy_playlists if emotion == "happy" else playlists
                    for link in all_links:
                        if link not in st.session_state.favorites:
                            st.session_state.favorites.append(link)
                    st.success("Added to favorites!")
            with col2:
                if st.button("👎 Dislike"):
                    st.info("We'll try to improve your experience!")
