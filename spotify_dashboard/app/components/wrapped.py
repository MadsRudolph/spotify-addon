import streamlit as st
import spotipy
import os
import json
import anthropic


def render_wrapped(sp: spotipy.Spotify):
    st.title("Your Wrapped")

    time_labels = {
        "Last 4 weeks": "short_term",
        "Last 6 months": "medium_term",
        "All time": "long_term",
    }
    range_label = st.selectbox("Period", list(time_labels.keys()), key="wrapped_range")
    time_range = time_labels[range_label]

    if st.button("Generate Wrapped", type="primary", use_container_width=True):
        st.session_state["wrapped_data"] = None
        st.session_state["wrapped_insights"] = None

    # Fetch data
    cache_key = f"wrapped_data_{time_range}"
    if cache_key not in st.session_state:
        with st.spinner("Gathering your listening data..."):
            try:
                data = _fetch_wrapped_data(sp, time_range)
                st.session_state[cache_key] = data
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")
                return

    data = st.session_state[cache_key]
    if not data:
        return

    top_tracks = data["top_tracks"]
    top_artists = data["top_artists"]
    recent = data["recent"]

    # -- Card 1: Your #1 Track --
    if top_tracks:
        track = top_tracks[0]
        img = track["album"]["images"][0]["url"] if track["album"]["images"] else ""
        artist_names = ", ".join(a["name"] for a in track["artists"])
        st.html(f"""
        <div class="wrapped-card wrapped-gradient-1">
            <div class="wrapped-label">Your #1 Track</div>
            <img src="{img}" class="wrapped-hero-img">
            <div class="wrapped-hero-title">{track['name']}</div>
            <div class="wrapped-hero-subtitle">{artist_names}</div>
        </div>
        """)

    # -- Card 2: Your #1 Artist --
    if top_artists:
        artist = top_artists[0]
        img = artist["images"][0]["url"] if artist.get("images") else ""
        st.html(f"""
        <div class="wrapped-card wrapped-gradient-2">
            <div class="wrapped-label">Your #1 Artist</div>
            <img src="{img}" class="wrapped-hero-img wrapped-round">
            <div class="wrapped-hero-title">{artist['name']}</div>
        </div>
        """)

    # -- Card 3: Top 5 Tracks --
    if len(top_tracks) >= 5:
        tracks_html = ""
        for i, t in enumerate(top_tracks[:5], 1):
            img = t["album"]["images"][-1]["url"] if t["album"]["images"] else ""
            artist = ", ".join(a["name"] for a in t["artists"])
            tracks_html += f"""
            <div class="wrapped-list-item">
                <span class="wrapped-list-rank">{i}</span>
                <img src="{img}" class="wrapped-list-img">
                <div class="wrapped-list-info">
                    <div class="wrapped-list-name">{t['name']}</div>
                    <div class="wrapped-list-sub">{artist}</div>
                </div>
            </div>
            """
        st.html(f"""
        <div class="wrapped-card wrapped-gradient-3">
            <div class="wrapped-label">Your Top 5 Tracks</div>
            {tracks_html}
        </div>
        """)

    # -- Card 4: Top 5 Artists --
    if len(top_artists) >= 5:
        artists_html = ""
        for i, a in enumerate(top_artists[:5], 1):
            img = a["images"][-1]["url"] if a.get("images") else ""
            artists_html += f"""
            <div class="wrapped-list-item">
                <span class="wrapped-list-rank">{i}</span>
                <img src="{img}" class="wrapped-list-img wrapped-round">
                <div class="wrapped-list-info">
                    <div class="wrapped-list-name">{a['name']}</div>
                </div>
            </div>
            """
        st.html(f"""
        <div class="wrapped-card wrapped-gradient-4">
            <div class="wrapped-label">Your Top 5 Artists</div>
            {artists_html}
        </div>
        """)

    # -- Card 5: Summary Stats --
    unique_artists = len({
        a["name"]
        for item in recent
        for a in item["track"]["artists"]
    })
    unique_tracks = len({item["track"]["id"] for item in recent})
    total_mins = sum(item["track"]["duration_ms"] for item in recent) // 60000

    st.html(f"""
    <div class="wrapped-card wrapped-gradient-5">
        <div class="wrapped-label">Recent Snapshot</div>
        <div class="wrapped-stats-grid">
            <div class="wrapped-stat">
                <div class="wrapped-stat-value">{len(recent)}</div>
                <div class="wrapped-stat-label">Tracks Played</div>
            </div>
            <div class="wrapped-stat">
                <div class="wrapped-stat-value">{unique_tracks}</div>
                <div class="wrapped-stat-label">Unique Tracks</div>
            </div>
            <div class="wrapped-stat">
                <div class="wrapped-stat-value">{unique_artists}</div>
                <div class="wrapped-stat-label">Artists</div>
            </div>
            <div class="wrapped-stat">
                <div class="wrapped-stat-value">{total_mins}</div>
                <div class="wrapped-stat-label">Minutes</div>
            </div>
        </div>
    </div>
    """)

    # -- Card 6: AI Personality / Insights --
    insights_key = f"wrapped_insights_{time_range}"
    if insights_key not in st.session_state:
        with st.spinner("Claude is analyzing your music taste..."):
            try:
                insights = _generate_insights(top_tracks, top_artists)
                st.session_state[insights_key] = insights
            except Exception as e:
                st.error(f"Failed to generate insights: {e}")
                st.session_state[insights_key] = None

    insights = st.session_state.get(insights_key)
    if insights:
        st.html(f"""
        <div class="wrapped-card wrapped-gradient-6">
            <div class="wrapped-label">Your Music Personality</div>
            <div class="wrapped-personality-type">{insights.get('personality', 'Music Lover')}</div>
            <div class="wrapped-personality-desc">{insights.get('description', '')}</div>
            <div class="wrapped-fun-facts">
                <div class="wrapped-label" style="margin-top: 20px;">Fun Facts</div>
                {''.join(f'<div class="wrapped-fact">• {fact}</div>' for fact in insights.get('fun_facts', []))}
            </div>
        </div>
        """)

    # Regenerate button
    if st.button("Regenerate Insights", key="regen_insights"):
        if insights_key in st.session_state:
            del st.session_state[insights_key]
        st.rerun()


def _fetch_wrapped_data(sp: spotipy.Spotify, time_range: str) -> dict:
    top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)["items"]
    top_artists = sp.current_user_top_artists(limit=50, time_range=time_range)["items"]
    recent = sp.current_user_recently_played(limit=50)["items"]
    return {
        "top_tracks": top_tracks,
        "top_artists": top_artists,
        "recent": recent,
    }


def _generate_insights(top_tracks: list, top_artists: list) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    track_names = [f"{t['name']} by {', '.join(a['name'] for a in t['artists'])}" for t in top_tracks[:20]]
    artist_names = [a["name"] for a in top_artists[:20]]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=(
            "You are a music personality analyst. Given a user's top tracks and artists, "
            "create a fun, engaging personality profile. "
            "Respond ONLY with valid JSON, no markdown. The JSON must have exactly these keys:\n"
            '- "personality": a creative 2-4 word personality type (e.g. "Midnight Groove Architect", "Indie Dream Drifter")\n'
            '- "description": a 2-3 sentence personality description that\'s fun and specific to their taste\n'
            '- "fun_facts": an array of 3-4 short, witty observations about their listening habits'
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Top tracks: {', '.join(track_names)}\n\n"
                f"Top artists: {', '.join(artist_names)}"
            ),
        }],
    )

    raw = response.content[0].text
    return json.loads(raw)
