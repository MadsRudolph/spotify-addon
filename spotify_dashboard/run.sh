#!/bin/sh

CONFIG_PATH=/data/options.json

export SPOTIFY_CLIENT_ID=$(jq -r '.spotify_client_id' "$CONFIG_PATH")
export SPOTIFY_CLIENT_SECRET=$(jq -r '.spotify_client_secret' "$CONFIG_PATH")
export ANTHROPIC_API_KEY=$(jq -r '.anthropic_api_key' "$CONFIG_PATH")
export SPOTIFY_REDIRECT_URI="http://127.0.0.1:8501/callback"

streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0
