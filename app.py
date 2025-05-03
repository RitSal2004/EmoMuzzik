import streamlit as st
import requests
from PIL import Image, ImageOps
import io

# Face++ API credentials
API_KEY = "_FQ9lRoO4yAtMRYdN-GwNEb49hTge24N"
API_SECRET = "favg_rbXiy3yT-1NZXaEr3g0Mgmix-GY"

# Emotion labels
emotion_labels = ['angry', 'sad', 'happy', 'neutral', 'surprise', 'fear', 'disgust']

# Static playlist mapping with 4–5 playlists per emotion
emotion_playlists = {
    "happy": [
        "https://open.spotify.com/playlist/2gSHA2hK9utrPK6ldtJgws",
        "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0",
        "https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC",
        "https://open.spotify.com/playlist/37i9dQZF1DWU0ScTcjJBdj",
        "https://open.spotify.com/playlist/1fF73hY1QzokhWz5RTeoRb"
    ],
    "sad": [
        "https://open.spotify.com/playlist/37i9dQZF1DWVrtsSlLKzro",
        "https://open.spotify.com/playlist/37i9dQZF1DX7qK8ma5wgG1",
        "https://open.spotify.com/playlist/37i9dQZF1DX7gIoKXt0gmx",
        "https://open.spotify.com/playlist/37i9dQZF1DWSqBruwoIXkA",
        "https://open.spotify.com/playlist/3ZgmfR6lsnCwdffZUan8EA"
    ],
    "angry": [
        "https://open.spotify.com/playlist/37i9dQZF1DWX83CujKHHOn",
        "https://open.spotify.com/playlist/37i9dQZF1DX3YSRoSdA634",
        "https://open.spotify.com/playlist/37i9dQZF1DWZJhOVGWqUKF",
        "https://open.spotify.com/playlist/37i9dQZF1DWWJOmJ7nRx0C",
        "https://open.spotify.com/playlist/4Pb0JtCwYcyTnW52yCu3PN"
    ],
    "neutral": [
        "https://open.spotify.com/playlist/37i9dQZF1DWUzFXarNiofw",
        "https://open.spotify.com/playlist/37i9dQZF1DWYBO1MoTDhZI",
        "https://open.spotify.com/playlist/37i9dQZF1DWVFeEut75IAL",
        "https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn",
        "https://open.spotify.com/playlist/37i9dQZF1DWSiZVO2J6WeI"
    ],
    "surprise": [
        "https://open.spotify.com/playlist/1EcICTdTjFDyS46OicRCZv",
        "https://open.spotify.com/playlist/37i9dQZF1DX2sUQwD7tbmL",
        "https://open.spotify.com/playlist/37i9dQZF1DXa2PvUpywmrr",
        "https://open.spotify.com/playlist/37i9dQZF1DWSIO2QWRavWZ",
        "https://open.spotify.com/playlist/37i9dQZF1DX2SK4ytI2KAZ"
    ],
    "fear": [
        "https://open.spotify.com/playlist/37i9dQZF1DWVIiR5qh2MFm",
        "https://open.spotify.com/playlist/37i9dQZF1DWZqd5JICZI0u",
        "https://open.spotify.com/playlist/37i9dQZF1DWXLeA8Omikj7",
        "https://open.spotify.com/playlist/37i9dQZF1DWU4EQPjP9ZpS",
        "https://open.spotify.com/playlist/37i9dQZF1DX1s9knjP51Oa"
    ],
    "disgust": [
        "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO",
        "https://open.spotify.com/playlist/37i9dQZF1DX1tyCD9QhIWF",
        "https://open.spotify.com/playlist/37i9dQZF1DX5gQonLbZD9s",
        "https://open.spotify.com/playlist/37i9dQZF1DWUvHZA1zLcjW",
        "https://open.spotify.com/playlist/37i9dQZF1DX4SBhb3fqCJd"
    ]
}

# Emotion detection using Face++
def get_emotion_from_faceplusplus(image):
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

# Streamlit UI
st.set_page_config(page_title="EmoMuzzik", page_icon="🎧")
st.title("🎭 Welcome to EmoMuzzik")
st.subheader("🎶 Your Emotion-Based Spotify Music Companion")

if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# Camera controls
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start Camera"):
        st.session_state.camera_active = True
with col2:
    if st.button("⏹️ Stop Camera"):
        st.session_state.camera_active = False

# Favorites section
with st.expander("⭐ My Favorite Tracks"):
    if st.session_state.favorites:
        for link in st.session_state.favorites:
            st.markdown(f"[Open Playlist]({link})")
            st.components.v1.iframe(link.replace("open.spotify.com", "open.spotify.com/embed"), height=80)
    else:
        st.info("No favorites yet!")

# Main app logic
if st.session_state.camera_active:
    img_file = st.camera_input("📸 Capture your photo")

    if img_file:
        img = Image.open(img_file)
        mirrored_img = ImageOps.mirror(img)
        st.image(mirrored_img, use_container_width=True)

        st.info("⏳ Detecting your emotion...")
        detected_emotion = get_emotion_from_faceplusplus(mirrored_img)

        selected_emotion = st.selectbox(
            "Detected Emotion (change if wrong):",
            options=emotion_labels,
            index=emotion_labels.index(detected_emotion)
        )
        emotion = selected_emotion
        st.subheader(f"🎯 Emotion: **{emotion.capitalize()}**")
        st.success("🎵 Recommended Playlists:")

        playlists = emotion_playlists.get(emotion, [])
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
                    st.info("Thanks for your feedback!")
