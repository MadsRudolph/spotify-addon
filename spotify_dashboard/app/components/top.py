import streamlit as st
import spotipy
from datetime import datetime

TIME_RANGES = {
    "Last 4 weeks": "short_term",
    "Last 6 months": "medium_term",
    "All time": "long_term",
}


def render_top(sp: spotipy.Spotify):
    st.title("Top Lists")

    view = st.radio(
        "View",
        ["Tracks", "Artists", "Recently Played"],
        horizontal=True,
        key="top_view",
    )

    if view == "Recently Played":
        _render_recently_played(sp)
    else:
        range_label = st.selectbox(
            "Time range",
            list(TIME_RANGES.keys()),
            key="top_range",
        )

        if view == "Tracks":
            _render_top_tracks(sp, TIME_RANGES[range_label])
        else:
            _render_top_artists(sp, TIME_RANGES[range_label])


def _render_top_tracks(sp: spotipy.Spotify, time_range: str):
    try:
        results = sp.current_user_top_tracks(limit=50, time_range=time_range)
    except Exception as e:
        st.error(f"Failed to load top tracks: {e}")
        return

    html = '<div class="list-container">'
    for i, track in enumerate(results["items"], 1):
        img = track["album"]["images"][-1]["url"] if track["album"]["images"] else ""
        artist_names = ", ".join(a["name"] for a in track["artists"])
        album_name = track["album"]["name"]

        html += f"""
        <div class="track-row">
            <div class="rank-num">{i}</div>
            <img src="{img}" class="track-img" alt="{track['name']}">
            <div class="track-info">
                <div class="track-name">{track['name']}</div>
                <div class="track-artist">{artist_names}</div>
            </div>
            <div class="track-extra">{album_name}</div>
        </div>
        """
    html += '</div>'
    st.html(html)


def _render_top_artists(sp: spotipy.Spotify, time_range: str):
    try:
        results = sp.current_user_top_artists(limit=50, time_range=time_range)
    except Exception as e:
        st.error(f"Failed to load top artists: {e}")
        return

    items = results["items"]
    html = '<div class="artist-grid">'
    for i, artist in enumerate(items, 1):
        img = artist["images"][0]["url"] if artist.get("images") else ""
        html += f"""
        <div class="artist-card" style="position: relative;">
            <div class="rank-num" style="position: absolute; top: 10px; left: 10px; font-size: 0.9em; z-index: 2;">#{i}</div>
            <img src="{img}" class="artist-img" alt="{artist['name']}">
            <div class="artist-name">{artist['name']}</div>
        </div>
        """
    html += '</div>'
    st.html(html)


def _render_recently_played(sp: spotipy.Spotify):
    try:
        results = sp.current_user_recently_played(limit=50)
    except Exception as e:
        st.error(f"Failed to load recently played: {e}")
        return

    filter_text = st.text_input("Filter by artist or track name", key="recent_filter")

    items = results["items"]
    if filter_text:
        ft = filter_text.lower()
        items = [
            item for item in items
            if ft in item["track"]["name"].lower()
            or any(ft in a["name"].lower() for a in item["track"]["artists"])
        ]

    html = '<div class="list-container">'
    for item in items:
        track = item["track"]
        played_at = datetime.fromisoformat(
            item["played_at"].replace("Z", "+00:00")
        ).strftime("%Y-%m-%d %H:%M")
        img = track["album"]["images"][-1]["url"] if track["album"]["images"] else ""
        artist_names = ", ".join(a["name"] for a in track["artists"])
        album_name = track["album"]["name"]

        html += f"""
        <div class="track-row">
            <div class="track-extra" style="width: 130px;">{played_at}</div>
            <img src="{img}" class="track-img" alt="{track['name']}">
            <div class="track-info">
                <div class="track-name">{track['name']}</div>
                <div class="track-artist">{artist_names}</div>
            </div>
            <div class="track-extra">{album_name}</div>
        </div>
        """
    html += '</div>'
    st.html(html)
