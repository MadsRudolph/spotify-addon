import streamlit as st
from spotify_auth import handle_auth

st.set_page_config(page_title="Spotify Dashboard", layout="wide")

sp = handle_auth()
if sp is None:
    st.stop()

# Store the Spotify client in session state for pages to use
st.session_state["sp"] = sp

tab_stats, tab_player, tab_playlist = st.tabs(["Stats", "Player", "Playlist Builder"])

with tab_stats:
    from pages.stats import render_stats
    render_stats(sp)

with tab_player:
    from pages.player import render_player
    render_player(sp)

with tab_playlist:
    from pages.playlist import render_playlist
    render_playlist(sp)
