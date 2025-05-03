import streamlit as st
import requests
from PIL import Image, ImageOps
import io
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Face++ API credentials
API_KEY = "_FQ9lRoO4yAtMRYdN-GwNEb49hTge24N"
API_SECRET = "favg_rbXiy3yT-1NZXaEr3g0Mgmix-GY"

# Emotion labels
emotion_labels = ['angry', 'sad', 'happy', 'neutral', 'surprise', 'fear', 'disgust']

# Happy playlists
happy_playlists = [
    "https://open.spotify.com/playlist/2gSHA2hK9utrPK6ldtJgws",
    "https://open.spotify.com/playlist/1fF73hY1QzokhWz5RTeoRb",
    "https://open.spotify.com/playlist/4F9XjRMCeyxlmysK16V85W"
]

# Queries for other emotions
emotion_queries = {
    "sad": ["sad songs", "melancholy vibes"],
    "angry": ["workout music", "rage tracks"],
    "surprise": ["eclectic mix", "unexpected hits"],
    "neutral": ["lofi chill", "study beats"],
    "fear": ["thriller soundtracks", "dark ambient"],
    "disgust": ["unusual soundscapes", "gritty tunes"]
}

# Spotify API auth
client_id = "3346818c664d48b09df8025c33b6e25c"
client_secret = "b2ebd040751049399d1f885a665ee606"
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


def search_spotify_playlists(query_list, limit=3):
    playlists = []
    if not query_list or not isinstance(query_list, list):
        return playlists

    for query in query_list:
        if not query.strip():
            continue
        try:
            results = sp.search(q=query, type='playlist', limit=limit)
            items = results.get('playlists', {}).get('items', [])
            for item in items:
                url = item.get('external_urls', {}).get('spotify')
                if url and url not in playlists:
                    playlists.append(url)
            if len(playlists) >= limit:
                break
        except Exception as e:
            st.error(f"🔍 Spotify Search Error: {e}")
    return playlists


def get_emotion_from_faceplusplus(image: Image.Image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    buffered.seek(0)

    url = "https://api-us.faceplusplus.com/facepp/v3/detect"
    files = {'image_file': buffered}
    params = {
        'api_key': API_KEY,
        'api_secret': API_SECRET,
        'return_attributes': 'emotion'
    }

    try:
        response = requests.post(url, files=files, data=params)
        data = response.json()

        if "faces" not in data or len(data["faces"]) == 0:
            st.warning("No faces detected — defaulting to neutral.")
            return "neutral"

        face = data["faces"][0]["attributes"]["emotion"]
        emotions = {
            "angry": face["anger"],
            "happy": face["happiness"],
            "sad": face["sadness"],
            "neutral": face["neutral"],
            "surprise": face["surprise"],
            "fear": face["fear"],
            "disgust": face["disgust"]
        }
        return max(emotions, key=emotions.get)

    except Exception as e:
        st.error(f"❌ Emotion detection failed: {e}")
        return "neutral"


# ---------- Streamlit UI ----------

st.set_page_config(page_title="EmoMuzzik", page_icon="🎧")
st.title("🎭 Welcome to EmoMuzzik")
st.subheader("🎶 Your Emotion-Based Spotify Music Companion")

if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "override_emotion" not in st.session_state:
    st.session_state.override_emotion = None

# Controls
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start Camera"):
        st.session_state.camera_active = True
with col2:
    if st.button("⏹️ Stop Camera"):
        st.session_state.camera_active = False

# Favorites view
with st.expander("⭐ My Favorite Tracks"):
    if st.session_state.favorites:
        for link in st.session_state.favorites:
            st.markdown(f"[Open Playlist]({link})")
            st.components.v1.iframe(link.replace("open.spotify.com", "open.spotify.com/embed"), height=80)
    else:
        st.info("No favorites yet!")

# Main functionality
if st.session_state.camera_active:
    img_file = st.camera_input("📸 Capture your photo")

    if img_file:
        img = Image.open(img_file)
        mirrored_img = ImageOps.mirror(img)
        st.image(mirrored_img, use_container_width=True)

        st.info("⏳ Detecting your emotion...")
        detected_emotion = get_emotion_from_faceplusplus(mirrored_img)

        # User can override
        selected_emotion = st.selectbox(
            "Detected Emotion (change if wrong):",
            options=emotion_labels,
            index=emotion_labels.index(detected_emotion)
        )
        st.session_state.override_emotion = selected_emotion
        emotion = selected_emotion

        st.subheader(f"🎯 Emotion: **{emotion.capitalize()}**")
        st.success(f"🎵 Recommended Playlists:")

        playlists = []
        if emotion == "happy":
            playlists = happy_playlists
        elif emotion in emotion_queries:
            playlists = search_spotify_playlists(emotion_queries.get(emotion, []))

        for link in playlists:
            st.markdown(f"[Open Playlist]({link})")
            st.components.v1.iframe(link.replace("open.spotify.com", "open.spotify.com/embed"), height=80)

        with st.expander("❤️ Like the recommendation?"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Like"):
                    for link in playlists:
                        if link not in st.session_state.favorites:
                            st.session_state.favorites.append(link)
                    st.success("Added to favorites!")
            with col2:
                if st.button("👎 Dislike"):
                    st.info("We’ll try to improve the recommendations!")
