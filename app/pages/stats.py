import streamlit as st
import spotipy
from datetime import datetime

TIME_RANGES = {
    "Last 4 weeks": "short_term",
    "Last 6 months": "medium_term",
    "All time": "long_term",
}


def render_stats(sp: spotipy.Spotify):
    st.header("Your Spotify Stats")

    col1, col2 = st.columns(2)

    # --- Top Tracks ---
    with col1:
        st.subheader("Top Tracks")
        range_label = st.selectbox(
            "Time range", list(TIME_RANGES.keys()), key="tracks_range"
        )
        try:
            results = sp.current_user_top_tracks(
                limit=20, time_range=TIME_RANGES[range_label]
            )
            for i, track in enumerate(results["items"], 1):
                img_url = track["album"]["images"][-1]["url"] if track["album"]["images"] else None
                artist_names = ", ".join(a["name"] for a in track["artists"])
                cols = st.columns([0.5, 1, 4])
                cols[0].write(f"**{i}**")
                if img_url:
                    cols[1].image(img_url, width=40)
                cols[2].write(f"**{track['name']}** — {artist_names}")
        except Exception as e:
            st.error(f"Failed to load top tracks: {e}")

    # --- Top Artists ---
    with col2:
        st.subheader("Top Artists")
        range_label_artists = st.selectbox(
            "Time range", list(TIME_RANGES.keys()), key="artists_range"
        )
        try:
            results = sp.current_user_top_artists(
                limit=20, time_range=TIME_RANGES[range_label_artists]
            )
            for i, artist in enumerate(results["items"], 1):
                img_url = artist["images"][-1]["url"] if artist["images"] else None
                cols = st.columns([0.5, 1, 4])
                cols[0].write(f"**{i}**")
                if img_url:
                    cols[1].image(img_url, width=40)
                cols[2].write(f"**{artist['name']}**")
        except Exception as e:
            st.error(f"Failed to load top artists: {e}")

    # --- Recently Played ---
    st.subheader("Recently Played")
    filter_text = st.text_input("Filter by artist or track name", key="recent_filter")

    try:
        results = sp.current_user_recently_played(limit=50)
        rows = []
        for item in results["items"]:
            track = item["track"]
            played_at = datetime.fromisoformat(
                item["played_at"].replace("Z", "+00:00")
            ).strftime("%Y-%m-%d %H:%M")
            artist_names = ", ".join(a["name"] for a in track["artists"])
            album_name = track["album"]["name"]
            rows.append(
                {
                    "Time": played_at,
                    "Track": track["name"],
                    "Artist": artist_names,
                    "Album": album_name,
                }
            )

        if filter_text:
            ft = filter_text.lower()
            rows = [
                r
                for r in rows
                if ft in r["Track"].lower() or ft in r["Artist"].lower()
            ]

        st.dataframe(rows, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Failed to load recently played: {e}")
