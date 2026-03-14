#!/bin/sh

CONFIG_PATH=/data/options.json

export SPOTIFY_CLIENT_ID=$(jq -r '.spotify_client_id' "$CONFIG_PATH")
export SPOTIFY_CLIENT_SECRET=$(jq -r '.spotify_client_secret' "$CONFIG_PATH")
export ANTHROPIC_API_KEY=$(jq -r '.anthropic_api_key' "$CONFIG_PATH")
export SPOTIFY_REDIRECT_URI=$(jq -r '.spotify_redirect_uri' "$CONFIG_PATH")

streamlit run app/main.py --server.port 8502 --server.address 0.0.0.0
