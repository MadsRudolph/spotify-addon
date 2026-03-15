import streamlit as st
import spotipy


def render_queue(sp: spotipy.Spotify):
    st.header("Queue")

    try:
        queue_data = sp.queue()
    except Exception as e:
        st.error(f"Failed to load queue: {e}")
        return

    currently_playing = queue_data.get("currently_playing")
    queue_items = queue_data.get("queue", [])

    if currently_playing:
        st.subheader("Now Playing")
        _display_track(currently_playing)
        st.divider()

    if not queue_items:
        st.info("Queue is empty.")
        return

    st.subheader(f"Up Next ({len(queue_items)} tracks)")
    html = '<div class="list-container">'
    for i, track in enumerate(queue_items, 1):
        img = track["album"]["images"][-1]["url"] if track.get("album", {}).get("images") else ""
        artist_names = ", ".join(a["name"] for a in track.get("artists", []))
        album_name = track.get("album", {}).get("name", "")
        
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


def _display_track(track):
    img = track["album"]["images"][0]["url"] if track.get("album", {}).get("images") else ""
    artist_names = ", ".join(a["name"] for a in track.get("artists", []))
    album_name = track.get("album", {}).get("name", "")
    
    st.html(f"""
    <div class="np-card" style="margin-bottom: 20px;">
        <img src="{img}" class="np-art" alt="{track['name']}">
        <div class="np-info">
            <div class="np-title">{track['name']}</div>
            <div class="np-artist">{artist_names}</div>
            <div class="np-album">{album_name}</div>
        </div>
    </div>
    """)
