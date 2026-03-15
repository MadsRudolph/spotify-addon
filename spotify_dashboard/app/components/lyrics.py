import streamlit as st
import spotipy
import urllib.request
import urllib.parse
import json
import re


def render_lyrics(sp: spotipy.Spotify):
    st.header("Lyrics")

    @st.fragment(run_every=1)
    def synced_lyrics():
        try:
            playback = sp.current_playback()
        except Exception as e:
            st.error(f"Failed to get playback: {e}")
            return

        if not playback or not playback.get("item"):
            st.info("Nothing is currently playing.")
            return

        track = playback["item"]
        track_name = track["name"]
        artist_name = track["artists"][0]["name"]
        album_name = track.get("album", {}).get("name", "")
        progress_ms = playback.get("progress_ms", 0)

        img = track["album"]["images"][0]["url"] if track["album"]["images"] else ""
        st.html(f"""
        <div class="np-card" style="margin-bottom: 20px; padding: 15px;">
            <img src="{img}" class="np-art" alt="{track_name}" style="width: 100px; height: 100px;">
            <div class="np-info">
                <div class="np-title" style="font-size: 1.4em;">{track_name}</div>
                <div class="np-artist" style="font-size: 1em;">{artist_name}</div>
                <div class="np-album" style="font-size: 0.8em;">{album_name}</div>
            </div>
        </div>
        """)

        st.divider()

        # Cache lyrics per track in session state
        cache_key = f"lyrics_{track_name}_{artist_name}"
        if cache_key not in st.session_state:
            raw = _fetch_lyrics(track_name, artist_name, album_name)
            if raw and _is_synced(raw):
                st.session_state[cache_key] = {"synced": True, "lines": _parse_lrc(raw)}
            elif raw:
                st.session_state[cache_key] = {"synced": False, "text": raw}
            else:
                st.session_state[cache_key] = None

        lyrics_data = st.session_state[cache_key]

        if lyrics_data is None:
            st.warning(f"No lyrics found for **{track_name}** by **{artist_name}**.")
            return

        if not lyrics_data["synced"]:
            st.text(lyrics_data["text"])
            return

        # Synced lyrics — highlight current line
        lines = lyrics_data["lines"]
        current_idx = _find_current_line(lines, progress_ms)

        html_parts = []
        for i, (ts_ms, text) in enumerate(lines):
            if not text.strip():
                html_parts.append("<br>")
                continue

            if i == current_idx:
                html_parts.append(
                    f'<div style="font-size:1.3em; font-weight:bold; color:#1DB954; '
                    f'padding:4px 0; transition:all 0.3s;">{text}</div>'
                )
            elif abs(i - current_idx) <= 2:
                html_parts.append(
                    f'<div style="font-size:1.1em; color:#b3b3b3; padding:2px 0;">{text}</div>'
                )
            else:
                html_parts.append(
                    f'<div style="font-size:1em; color:#535353; padding:2px 0;">{text}</div>'
                )

        st.html("".join(html_parts))

    synced_lyrics()


def _parse_lrc(lrc_text: str) -> list[tuple[int, str]]:
    """Parse LRC format into list of (timestamp_ms, text)."""
    lines = []
    pattern = re.compile(r"\[(\d{2}):(\d{2})\.(\d{2,3})\]\s*(.*)")
    for line in lrc_text.split("\n"):
        m = pattern.match(line.strip())
        if m:
            mins, secs, ms_part = int(m.group(1)), int(m.group(2)), m.group(3)
            ms = int(ms_part) * (10 if len(ms_part) == 2 else 1)
            total_ms = mins * 60000 + secs * 1000 + ms
            lines.append((total_ms, m.group(4)))
    return lines


def _is_synced(text: str) -> bool:
    return bool(re.search(r"\[\d{2}:\d{2}\.\d{2,3}\]", text))


def _find_current_line(lines: list[tuple[int, str]], progress_ms: int) -> int:
    current = 0
    for i, (ts_ms, _) in enumerate(lines):
        if ts_ms <= progress_ms:
            current = i
        else:
            break
    return current


def _fetch_lyrics(track: str, artist: str, album: str) -> str | None:
    params = urllib.parse.urlencode({
        "track_name": track,
        "artist_name": artist,
        "album_name": album,
    })
    url = f"https://lrclib.net/api/get?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SpotifyDashboard/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return data.get("syncedLyrics") or data.get("plainLyrics")
    except Exception:
        return _search_lyrics(track, artist)


def _search_lyrics(track: str, artist: str) -> str | None:
    params = urllib.parse.urlencode({"q": f"{track} {artist}"})
    url = f"https://lrclib.net/api/search?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SpotifyDashboard/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            results = json.loads(resp.read().decode())
            if results:
                return results[0].get("syncedLyrics") or results[0].get("plainLyrics")
    except Exception:
        pass
    return None
