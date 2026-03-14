# Spotify Dashboard — Documentation

## Prerequisites

1. A **Spotify Developer** account with a registered app at [developer.spotify.com](https://developer.spotify.com)
2. An **Anthropic API key** for the AI playlist builder

## Spotify App Setup

1. Go to your [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app (or use an existing one)
3. Add `http://127.0.0.1:8502/callback` as a **Redirect URI**
4. Copy your **Client ID** and **Client Secret**

## Addon Configuration

| Option | Description |
|---|---|
| `spotify_client_id` | Your Spotify app Client ID |
| `spotify_client_secret` | Your Spotify app Client Secret |
| `anthropic_api_key` | Your Anthropic API key (for playlist builder) |

## Usage

After starting the addon, open the Web UI. On first launch you will be asked to log in with your Spotify account.

### Stats Tab
Browse your top tracks and artists across three time ranges (4 weeks, 6 months, all time) and see your 50 most recently played tracks with a text filter.

### Player Tab
See what is currently playing with album art, progress, and full playback controls. Switch between Spotify Connect devices with the device selector. The player auto-refreshes every 5 seconds.

### Playlist Builder Tab
Describe a mood or context (e.g. "late night soldering session, focus, electronic but not aggressive"), set a track count, and optionally provide seed artists. Claude suggests tracks, which are matched against Spotify. Deselect any you don't want, name the playlist, and create it directly in your Spotify library.

## Troubleshooting

- **"No active Spotify devices found"** — Open Spotify on any device first, then refresh the player tab.
- **Login redirect fails** — Make sure `http://127.0.0.1:8502/callback` is added as a redirect URI in your Spotify Developer Dashboard.
- **Claude API errors** — Verify your Anthropic API key is correct in the addon configuration.
