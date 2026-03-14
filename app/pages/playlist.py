import streamlit as st
import spotipy
from llm import generate_playlist


def render_playlist(sp: spotipy.Spotify):
    st.header("AI Playlist Builder")

    # --- User Inputs ---
    vibe = st.text_area(
        "Describe the vibe or context for your playlist",
        placeholder="e.g. late night soldering session, focus, electronic but not aggressive",
        key="vibe_input",
    )
    col1, col2 = st.columns(2)
    with col1:
        n_tracks = st.number_input(
            "Number of tracks", min_value=5, max_value=30, value=15, key="n_tracks"
        )
    with col2:
        seed_artists = st.text_input(
            "Seed artists (optional, comma-separated)", key="seed_artists"
        )

    if st.button("Generate Playlist", key="generate_btn"):
        if not vibe.strip():
            st.warning("Please describe a vibe first.")
            return

        with st.spinner("Asking Claude for track suggestions..."):
            try:
                tracks, playlist_name = generate_playlist(
                    vibe, n_tracks, seed_artists if seed_artists.strip() else None
                )
            except Exception as e:
                st.error(f"Claude API error: {e}")
                return

        st.session_state["suggested_tracks"] = tracks
        st.session_state["playlist_name"] = playlist_name
        st.session_state["matched_tracks"] = None

    # --- Display Suggestions & Match on Spotify ---
    if "suggested_tracks" in st.session_state and st.session_state["suggested_tracks"]:
        tracks = st.session_state["suggested_tracks"]

        st.subheader("Claude's Suggestions")
        for t in tracks:
            st.write(f"- **{t['track']}** — {t['artist']}")

        # Search Spotify for matches
        if st.session_state.get("matched_tracks") is None:
            matched = []
            with st.spinner("Searching Spotify for matches..."):
                for t in tracks:
                    query = f"track:{t['track']} artist:{t['artist']}"
                    try:
                        results = sp.search(q=query, type="track", limit=1)
                        items = results["tracks"]["items"]
                        if items:
                            matched.append(
                                {
                                    "uri": items[0]["uri"],
                                    "name": items[0]["name"],
                                    "artist": ", ".join(
                                        a["name"] for a in items[0]["artists"]
                                    ),
                                    "image": (
                                        items[0]["album"]["images"][-1]["url"]
                                        if items[0]["album"]["images"]
                                        else None
                                    ),
                                    "found": True,
                                }
                            )
                        else:
                            matched.append(
                                {
                                    "uri": None,
                                    "name": t["track"],
                                    "artist": t["artist"],
                                    "image": None,
                                    "found": False,
                                }
                            )
                    except Exception:
                        matched.append(
                            {
                                "uri": None,
                                "name": t["track"],
                                "artist": t["artist"],
                                "image": None,
                                "found": False,
                            }
                        )
            st.session_state["matched_tracks"] = matched

        # Display matched tracks with checkboxes
        st.subheader("Spotify Matches")
        matched = st.session_state["matched_tracks"]
        selected = []

        for i, m in enumerate(matched):
            cols = st.columns([0.5, 1, 4, 1])
            checked = cols[0].checkbox(
                "sel",
                value=m["found"],
                key=f"track_sel_{i}",
                label_visibility="hidden",
            )
            if m["image"]:
                cols[1].image(m["image"], width=40)
            cols[2].write(f"**{m['name']}** — {m['artist']}")
            if not m["found"]:
                cols[3].write("🚫 Not found")
            if checked and m["found"]:
                selected.append(m["uri"])

        # --- Create Playlist ---
        st.divider()
        playlist_name = st.text_input(
            "Playlist name",
            value=st.session_state.get("playlist_name", "My Playlist"),
            key="final_playlist_name",
        )

        if st.button("Create Playlist", key="create_btn"):
            if not selected:
                st.warning("No tracks selected.")
                return

            try:
                user_id = sp.current_user()["id"]
                new_playlist = sp.user_playlist_create(
                    user_id, playlist_name, public=False
                )
                sp.playlist_add_items(new_playlist["id"], selected)
                st.success(f"Playlist **{playlist_name}** created with {len(selected)} tracks!")
                spotify_url = new_playlist["external_urls"]["spotify"]
                st.markdown(f"[Open in Spotify]({spotify_url})")
                st.code(new_playlist["uri"], language=None)
            except Exception as e:
                st.error(f"Failed to create playlist: {e}")
