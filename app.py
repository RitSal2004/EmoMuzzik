import streamlit as st
import requests
from PIL import Image, ImageOps
import io
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Face++ API credentials (replace with your credentials)
API_KEY = "_FQ9lRoO4yAtMRYdN-GwNEb49hTge24N"
API_SECRET = "favg_rbXiy3yT-1NZXaEr3g0Mgmix-GY"

# Emotion labels supported by Face++ API
emotion_labels = ['angry', 'sad', 'happy', 'neutral', 'surprise', 'fear', 'disgust']

# Predefined Happy Playlists
happy_playlists = [
    "https://open.spotify.com/playlist/2gSHA2hK9utrPK6ldtJgws",
    "https://open.spotify.com/playlist/1fF73hY1QzokhWz5RTeoRb",
    "https://open.spotify.com/playlist/4F9XjRMCeyxlmysK16V85W"
]

# Other emotion mappings (including fear and disgust)
emotion_queries = {
    "sad": ["sad songs", "melancholy vibes", "emotional music", "slow songs"],
    "angry": "workout music",
    "surprise": ["Unexpected hits", "eclectic mix", "surprise music", "mood shifts"],
    "neutral": ["calm lofi", "chill beats", "study music", "relaxing vibes"],
    "fear": ["intense music", "thriller soundtrack", "suspense music"],
    "disgust": ["unpleasant sounds", "dark moods", "creepy music"]
}

# Spotify Credentials
client_id = "3346818c664d48b09df8025c33b6e25c"
client_secret = "b2ebd040751049399d1f885a665ee606"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

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

# Face++ API for emotion detection
def get_emotion_from_faceplusplus(image: Image.Image):
    # Convert the image to byte format
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    buffered.seek(0)

    # Prepare the data for the Face++ API
    url = "https://api-us.faceplusplus.com/facepp/v3/detect"
    files = {
        'image_file': buffered
    }
    params = {
        'api_key': API_KEY,
        'api_secret': API_SECRET,
        'return_attributes': 'emotion'
    }

    try:
        # Make the API request
        response = requests.post(url, files=files, data=params)
        data = response.json()

        if "faces" not in data or len(data["faces"]) == 0:
            st.warning("No faces detected, defaulting to neutral.")
            return "neutral"

        # Extract emotions from the response
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

        # Determine the emotion with the highest score
        detected_emotion = max(emotions, key=emotions.get)
        return detected_emotion

    except Exception as e:
        st.error(f"❌ Emotion detection failed: {e}")
        return "neutral"

# Streamlit UI
st.set_page_config(page_title="EmoMuzzik", page_icon="🎧")
st.title("🎭 Welcome to EmoMuzzik")
st.subheader("🎶 Your Emotion-Based Spotify Music Companion")

if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "override_emotion" not in st.session_state:
    st.session_state.override_emotion = None
if "emotion_changed" not in st.session_state:
    st.session_state.emotion_changed = False

col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start Camera"):
        st.session_state.camera_active = True
with col2:
    if st.button("⏹️ Stop Camera"):
        st.session_state.camera_active = False

# View Favorites
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

        st.info("⏳ Sending image to Face++ API...")
        detected_emotion = get_emotion_from_faceplusplus(mirrored_img)

        st.session_state.override_emotion = st.selectbox(
            "Change Emotion (if incorrect):",
            options=emotion_labels,
            index=emotion_labels.index(detected_emotion) if detected_emotion in emotion_labels else emotion_labels.index("neutral")
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
                    if emotion == "happy":
                        for link in happy_playlists:
                            if link not in st.session_state.favorites:
                                st.session_state.favorites.append(link)
                    else:
                        for link in playlists:
                            if link not in st.session_state.favorites:
                                st.session_state.favorites.append(link)
                    st.success("Added to favorites!")
            with col2:
                if st.button("👎 Dislike"):
                    st.info("We'll try to improve your experience!")