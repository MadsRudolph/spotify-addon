import os
import json
import anthropic

SYSTEM_PROMPT = (
    "You are a music curator. The user will describe a vibe or context. "
    "Respond ONLY with a valid JSON array. No markdown, no explanation, "
    "no preamble. Each item must have exactly two keys: 'track' and 'artist'. "
    'Example: [{"track": "So What", "artist": "Miles Davis"}]'
)


def generate_playlist(
    vibe: str, n_tracks: int, seed_artists: str | None = None
) -> tuple[list[dict], str]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_msg = (
        f"Create a playlist of exactly {n_tracks} tracks for this vibe: {vibe}\n"
    )
    if seed_artists:
        user_msg += f"Seed artists for inspiration (but don't only use these): {seed_artists}\n"
    user_msg += (
        "Also suggest a short, creative playlist name. Return it as the FIRST "
        'element in the array with a single key "playlist_name". '
        "The remaining elements should each have 'track' and 'artist' keys."
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = response.content[0].text
    data = json.loads(raw)

    playlist_name = "My Playlist"
    tracks = []
    for item in data:
        if "playlist_name" in item:
            playlist_name = item["playlist_name"]
        elif "track" in item and "artist" in item:
            tracks.append(item)

    return tracks, playlist_name
