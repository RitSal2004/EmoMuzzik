import streamlit as st
from deepface import DeepFace
from PIL import Image, ImageOps
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Emotion labels
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

# Predefined playlist URLs for Happy Emotion
happy_playlists = [
    "https://open.spotify.com/playlist/2gSHA2hK9utrPK6ldtJgws",  # Example Happy Playlist 1
    "https://open.spotify.com/playlist/1fF73hY1QzokhWz5RTeoRb",  # Example Happy Playlist 2
    "https://open.spotify.com/playlist/4F9XjRMCeyxlmysK16V85W"   # Example Happy Playlist 3
]

# Spotify-friendly emotion-to-query mapping for other emotions
emotion_queries = {
    "sad": ["sad songs", "sad music", "melancholy vibes", "emotional music", "slow songs"],
    "angry": "Heavy music",
    "fear": ["dark cinematic", "horror soundtrack", "suspense music", "creepy beats"],
    "surprise": ["Unexpected hits", "eclectic mix", "surprise music", "mood shifts"],
    "disgust": ["grunge punk", "punk rock", "heavy metal", "edgy tracks"],
    "neutral": ["calm lofi", "chill beats", "study music", "relaxing vibes"]
}

# Spotify API setup
client_id = "3346818c664d48b09df8025c33b6e25c"
client_secret = "b2ebd040751049399d1f885a665ee606"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

def search_spotify_playlists(query_list, limit=3):
    playlists = []
    for query in query_list:
        try:
            results = sp.search(q=query, type='playlist', limit=limit)
            # Ensure the response contains valid 'playlists' data
            if 'playlists' in results and 'items' in results['playlists']:
                items = results['playlists']['items']
                for item in items:
                    if 'external_urls' in item:
                        playlists.append(item['external_urls']['spotify'])
            if len(playlists) >= limit:
                break  # Stop searching once we've found enough playlists
        except Exception as e:
            st.error(f"🔍 Spotify Search Error: {e}")
    
    # Return an empty list if no playlists found
    if not playlists:
        st.warning("😕 No playlists found for this emotion. Try another or check your internet connection.")
    return playlists

# Streamlit app setup
st.set_page_config(page_title="EmoMuzzik", page_icon="🎧")
st.title("🎭 Welcome to EmoMuzzik")
st.subheader("🎶 Your Emotion-Based Spotify Music Companion")

# Session state
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "override_emotion" not in st.session_state:
    st.session_state.override_emotion = None
if "emotion_changed" not in st.session_state:
    st.session_state.emotion_changed = False

# Camera control
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

# Emotion detection
if st.session_state.camera_active:
    img_file = st.camera_input("📸 Capture a photo")

    if img_file is not None:
        img = Image.open(img_file)

        # ✅ Mirror the image
        mirrored_img = ImageOps.mirror(img)
        st.image(mirrored_img, use_container_width=True)

        img_np = np.array(mirrored_img)
        st.info("⏳ Detecting emotion with DeepFace...")

        try:
            result = DeepFace.analyze(img_path=img_np, actions=["emotion"], enforce_detection=False)
            detected_emotion = result[0]["dominant_emotion"].lower()

            # Emotion override
            st.session_state.override_emotion = st.selectbox(
                "Change Emotion (if incorrect):",
                options=emotion_labels,
                index=emotion_labels.index(detected_emotion)
            )

            # Check if emotion was changed
            st.session_state.emotion_changed = (st.session_state.override_emotion != detected_emotion)

            emotion = st.session_state.override_emotion
            st.subheader(f"🎯 Final Emotion Selected: **{emotion.capitalize()}**")

            if st.session_state.emotion_changed:
                st.caption("🙇 Sorry if we detected the wrong emotion — we're still working on improving accuracy!")

            # Show music recommendations
            if emotion == "happy":
                st.success(f"🎶 Recommended Playlists for **{emotion.capitalize()}**:")
                # Show predefined playlists for "happy"
                for link in happy_playlists:
                    st.markdown(f"[Open Playlist]({link})")
                    st.components.v1.iframe(link.replace("open.spotify.com", "open.spotify.com/embed"), height=80)

            elif emotion in emotion_queries:
                st.success(f"🎶 Recommended Playlists for **{emotion.capitalize()}**:")
                queries = emotion_queries[emotion]
                playlists = search_spotify_playlists(queries)

                if playlists:
                    for link in playlists:
                        st.markdown(f"[Open Playlist]({link})")
                        st.components.v1.iframe(link.replace("open.spotify.com", "open.spotify.com/embed"), height=80)

                    with st.expander("❤️ Did you like the recommendation?"):
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("👍 Like"):
                                for link in playlists:
                                    if link not in st.session_state.favorites:
                                        st.session_state.favorites.append(link)
                                st.success("Added to favorites!")
                        with col2:
                            if st.button("👎 Dislike"):
                                st.info("We'll try to improve your experience!")

        except Exception as e:
            st.error(f"😓 Something went wrong: {e}")