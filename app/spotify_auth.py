import os
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPES = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "user-top-read "
    "user-read-recently-played "
    "playlist-modify-public "
    "playlist-modify-private"
)

CACHE_PATH = "/data/.spotify_cache"


def _get_auth_manager() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
        scope=SCOPES,
        cache_path=CACHE_PATH,
        show_dialog=False,
    )


def handle_auth() -> spotipy.Spotify | None:
    auth_manager = _get_auth_manager()

    # Handle callback with auth code in query params
    query_params = st.query_params
    code = query_params.get("code")
    if code:
        auth_manager.get_access_token(code, as_dict=False)
        st.query_params.clear()
        st.rerun()

    # Check for cached token
    token_info = auth_manager.cache_handler.get_cached_token()
    if not token_info:
        auth_url = auth_manager.get_authorize_url()
        st.title("Spotify Dashboard")
        st.markdown("Connect your Spotify account to get started.")
        st.link_button("Log in with Spotify", auth_url)
        return None

    # Refresh if expired
    if auth_manager.is_token_expired(token_info):
        token_info = auth_manager.refresh_access_token(token_info["refresh_token"])

    return spotipy.Spotify(auth=token_info["access_token"])
