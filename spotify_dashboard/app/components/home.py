import streamlit as st
import spotipy
from datetime import datetime


def render_home(sp: spotipy.Spotify):
    # User profile header
    try:
        me = sp.me()
        profile_name = me.get("display_name", "User")
        profile_img = me["images"][0]["url"] if me.get("images") else None
    except Exception:
        profile_name = "User"
        profile_img = None

    col_profile, col_greeting = st.columns([1, 5])
    with col_profile:
        if profile_img:
            st.image(profile_img, width=80)
    with col_greeting:
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        st.title(f"{greeting}, {profile_name}")

    st.divider()

    # Summary stats from recently played
    try:
        recent = sp.current_user_recently_played(limit=50)
        recent_items = recent["items"]
    except Exception:
        recent_items = []

    total_tracks = len(recent_items)
    unique_artists = len({
        a["name"]
        for item in recent_items
        for a in item["track"]["artists"]
    })
    total_ms = sum(item["track"]["duration_ms"] for item in recent_items)
    total_mins = total_ms // 60000

    c1, c2, c3 = st.columns(3)
    with c1:
        st.html(f"""
        <div class="stat-card">
            <div class="stat-value">{total_tracks}</div>
            <div class="stat-label">Recent Tracks</div>
        </div>
        """)
    with c2:
        st.html(f"""
        <div class="stat-card">
            <div class="stat-value">{unique_artists}</div>
            <div class="stat-label">Unique Artists</div>
        </div>
        """)
    with c3:
        st.html(f"""
        <div class="stat-card">
            <div class="stat-value">{total_mins}</div>
            <div class="stat-label">Minutes Played</div>
        </div>
        """)

    st.write("")

    # Now playing card
    try:
        playback = sp.current_playback()
        if playback and playback.get("item"):
            track = playback["item"]
            st.subheader("Now Playing")
            
            img = track["album"]["images"][0]["url"] if track["album"]["images"] else ""
            artist_names = ", ".join(a["name"] for a in track["artists"])
            album_name = track["album"]["name"]
            st.html(f"""
            <div class="np-card">
                <img src="{img}" class="np-art" alt="{track['name']}">
                <div class="np-info">
                    <div class="np-title">{track['name']}</div>
                    <div class="np-artist">{artist_names}</div>
                    <div class="np-album">{album_name}</div>
                </div>
            </div>
            """)
            
            progress = playback.get("progress_ms", 0)
            duration = track.get("duration_ms", 1)
            st.progress(progress / duration)
    except Exception:
        pass

    st.write("")

    # Top artists preview (short term)
    try:
        top_artists = sp.current_user_top_artists(limit=5, time_range="short_term")
        if top_artists["items"]:
            st.subheader("Your Top Artists — Last 4 Weeks")
            html = '<div class="artist-grid">'
            for artist in top_artists["items"]:
                img = artist["images"][0]["url"] if artist.get("images") else ""
                html += f"""
                <div class="artist-card">
                    <img src="{img}" class="artist-img" alt="{artist['name']}">
                    <div class="artist-name">{artist['name']}</div>
                </div>
                """
            html += '</div>'
            st.html(html)
    except Exception:
        pass

    st.write("")

    # Top tracks preview (short term)
    try:
        top_tracks = sp.current_user_top_tracks(limit=5, time_range="short_term")
        if top_tracks["items"]:
            st.subheader("Your Top Tracks — Last 4 Weeks")
            html = '<div class="list-container">'
            for i, track in enumerate(top_tracks["items"], 1):
                img = track["album"]["images"][-1]["url"] if track["album"]["images"] else ""
                artist_names = ", ".join(a["name"] for a in track["artists"])
                html += f"""
                <div class="track-row">
                    <div class="rank-num">{i}</div>
                    <img src="{img}" class="track-img" alt="{track['name']}">
                    <div class="track-info">
                        <div class="track-name">{track['name']}</div>
                        <div class="track-artist">{artist_names}</div>
                    </div>
                </div>
                """
            html += '</div>'
            st.html(html)
    except Exception:
        pass

    st.write("")

    # Recently played
    if recent_items:
        st.subheader("Recently Played")
        html = '<div class="list-container">'
        for item in recent_items[:15]:
            track = item["track"]
            played_at = datetime.fromisoformat(
                item["played_at"].replace("Z", "+00:00")
            ).strftime("%H:%M")
            img = track["album"]["images"][-1]["url"] if track["album"]["images"] else ""
            artist_names = ", ".join(a["name"] for a in track["artists"])
            html += f"""
            <div class="track-row">
                <div class="track-extra" style="width: 50px;">{played_at}</div>
                <img src="{img}" class="track-img" alt="{track['name']}">
                <div class="track-info">
                    <div class="track-name">{track['name']}</div>
                    <div class="track-artist">{artist_names}</div>
                </div>
            </div>
            """
        html += '</div>'
        st.html(html)
