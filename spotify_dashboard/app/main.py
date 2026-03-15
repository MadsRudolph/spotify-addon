import streamlit as st
from spotify_auth import handle_auth

st.set_page_config(
    page_title="Spotify Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path, "r") as f:
        st.html(f"<style>{f.read()}</style>")

load_css()

sp = handle_auth()
if sp is None:
    st.stop()

# Sidebar navigation
with st.sidebar:
    st.title("🎵 Spotify Dashboard")
    st.divider()

    pages = {
        "Home": "🏠",
        "Top": "📊",
        "Player": "🎧",
        "Queue": "📋",
        "Lyrics": "🎤",
        "Genres": "🎸",
        "Wrapped": "🎁",
        "Playlist Builder": "🤖",
    }

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home"

    for page, icon in pages.items():
        if st.button(
            f"{icon}  {page}",
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if st.session_state["current_page"] == page else "secondary",
        ):
            st.session_state["current_page"] = page
            st.rerun()

# Render current page
page = st.session_state["current_page"]

if page == "Home":
    from components.home import render_home
    render_home(sp)
elif page == "Top":
    from components.top import render_top
    render_top(sp)
elif page == "Player":
    from components.player import render_player
    render_player(sp)
elif page == "Queue":
    from components.queue import render_queue
    render_queue(sp)
elif page == "Lyrics":
    from components.lyrics import render_lyrics
    render_lyrics(sp)
elif page == "Genres":
    from components.genres import render_genres
    render_genres(sp)
elif page == "Wrapped":
    from components.wrapped import render_wrapped
    render_wrapped(sp)
elif page == "Playlist Builder":
    from components.playlist import render_playlist
    render_playlist(sp)
