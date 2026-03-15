import streamlit as st
import spotipy
import os
import json
import anthropic

TIME_RANGES = {
    "Last 4 weeks": "short_term",
    "Last 6 months": "medium_term",
    "All time": "long_term",
}


def render_genres(sp: spotipy.Spotify):
    st.title("Genre Breakdown")

    range_label = st.selectbox(
        "Time range", list(TIME_RANGES.keys()), key="genre_range"
    )

    try:
        results = sp.current_user_top_artists(
            limit=50, time_range=TIME_RANGES[range_label]
        )
    except Exception as e:
        st.error(f"Failed to load top artists: {e}")
        return

    artists = [a["name"] for a in results["items"]]
    if not artists:
        st.info("No top artists found for this time range.")
        return

    cache_key = f"genre_analysis_{range_label}"

    if cache_key not in st.session_state:
        with st.spinner("Analyzing your top artists' genres with Claude..."):
            try:
                genre_data = _classify_genres(artists)
                st.session_state[cache_key] = genre_data
            except Exception as e:
                st.error(f"Failed to analyze genres: {e}")
                return

    genre_data = st.session_state[cache_key]

    # Bar chart
    import pandas as pd

    import altair as alt

    sorted_genres = sorted(genre_data.items(), key=lambda x: x[1], reverse=True)
    top_genres = sorted_genres[:15]

    df = pd.DataFrame({"Genre": [g[0] for g in top_genres], "Artists": [g[1] for g in top_genres]})
    
    chart = alt.Chart(df).mark_bar(color="#1DB954", cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("Genre", sort="-y", axis=alt.Axis(labelColor="#b3b3b3", titleColor="#ffffff")),
        y=alt.Y("Artists", axis=alt.Axis(labelColor="#b3b3b3", titleColor="#ffffff")),
        tooltip=["Genre", "Artists"]
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        gridColor="rgba(255, 255, 255, 0.05)"
    ).properties(
        background="transparent"
    )
    st.altair_chart(chart, use_container_width=True)

    # Full list
    st.subheader("All Genres")
    html = '<div class="list-container" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 15px;">'
    for genre, count in sorted_genres:
        html += f'<div style="background: rgba(255,255,255,0.05); padding: 10px 15px; border-radius: 8px;"><strong>{genre}</strong> — {count} artist{"s" if count > 1 else ""}</div>'
    html += '</div>'
    st.html(html)

    if st.button("Re-analyze", key="genre_reanalyze"):
        del st.session_state[cache_key]
        st.rerun()


def _classify_genres(artists: list[str]) -> dict[str, int]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    artist_list = ", ".join(artists)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=(
            "You are a music expert. Given a list of artists, classify each into "
            "one primary genre. Use broad but meaningful genre names (e.g. 'Jazz', "
            "'Hip Hop', 'Electronic', 'R&B', 'Rock', 'Pop', 'Classical', 'Indie', "
            "'Metal', 'Folk', 'Latin', 'Soul', 'Funk', 'Country', 'Ambient'). "
            "Respond ONLY with a valid JSON object mapping genre names to artist counts. "
            "No markdown, no explanation. Example: {\"Jazz\": 5, \"Hip Hop\": 3}"
        ),
        messages=[{"role": "user", "content": f"Classify these artists: {artist_list}"}],
    )

    raw = response.content[0].text
    return json.loads(raw)
