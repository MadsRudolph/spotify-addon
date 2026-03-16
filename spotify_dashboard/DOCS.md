# Spotify Dashboard — Documentation

## Prerequisites

1. A **Spotify Developer** account with a registered app at [developer.spotify.com](https://developer.spotify.com)
2. An **Anthropic API key** for the AI playlist builder

## Spotify App Setup

1. Go to your [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app (or use an existing one)
3. Add your redirect URI — see Access Methods below for which URL to use
4. Copy your **Client ID** and **Client Secret**

## Addon Configuration

| Option | Required | Description |
|---|---|---|
| `spotify_client_id` | Yes | Your Spotify app Client ID |
| `spotify_client_secret` | Yes | Your Spotify app Client Secret |
| `anthropic_api_key` | Yes | Your Anthropic API key (for playlist builder) |
| `spotify_redirect_uri` | Yes | OAuth redirect URI — must match exactly what you registered in Spotify |

## Access Methods

The addon serves HTTPS using an auto-generated self-signed certificate. You will need to accept a browser security warning on first visit.

### Via Tailscale

Set `spotify_redirect_uri` to:
```
https://homeassistant.taile8312d.ts.net:8502/callback
```

Register the same URI in your Spotify Developer Dashboard, then access the dashboard at:
```
https://homeassistant.taile8312d.ts.net:8502
```

### Via local network

Set `spotify_redirect_uri` to:
```
https://<raspberry-pi-ip>:8502/callback
```

Register the same URI in Spotify, then access at `https://<raspberry-pi-ip>:8502`.

### Why HTTPS?

Spotify requires all non-loopback redirect URIs to use HTTPS. The addon auto-generates a self-signed TLS certificate on first startup (stored in `/data/tls/`). You only need to accept the browser warning once.

## Usage

After starting the addon, open the Web UI. On first launch you will be asked to log in with your Spotify account.

### Home
Overview of your profile and current listening activity.

### Top
Browse your top tracks and artists across three time ranges (4 weeks, 6 months, all time).

### Player
See what is currently playing with album art, progress, and full playback controls. Switch between Spotify Connect devices. Auto-refreshes every 5 seconds.

### Queue
View and manage your current playback queue.

### Lyrics
View lyrics for the currently playing track.

### Genres
Explore your listening habits by genre.

### Wrapped
Your personal listening summary, stats.fm-style.

### Playlist Builder
Describe a mood or context, set a track count, and optionally provide seed artists. Claude suggests tracks, which are matched against Spotify. Deselect any you don't want, name the playlist, and create it directly in your library.

## Troubleshooting

- **"No active Spotify devices found"** — Open Spotify on any device first, then refresh.
- **Login redirect fails** — Make sure the redirect URI in your Spotify Developer Dashboard matches `spotify_redirect_uri` exactly. Check addon logs for `Redirect URI: ...`.
- **Browser security warning** — Expected with the self-signed certificate. Click "Advanced" → "Proceed" (Chrome) or "Accept the Risk" (Firefox).
- **Claude API errors** — Verify your Anthropic API key is correct.
