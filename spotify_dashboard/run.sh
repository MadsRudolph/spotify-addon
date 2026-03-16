#!/bin/sh

CONFIG_PATH=/data/options.json
CERT_DIR=/data/tls

export SPOTIFY_CLIENT_ID=$(jq -r '.spotify_client_id' "$CONFIG_PATH")
export SPOTIFY_CLIENT_SECRET=$(jq -r '.spotify_client_secret' "$CONFIG_PATH")
export ANTHROPIC_API_KEY=$(jq -r '.anthropic_api_key' "$CONFIG_PATH")
export SPOTIFY_REDIRECT_URI=$(jq -r '.spotify_redirect_uri' "$CONFIG_PATH")

# Generate self-signed TLS cert if none exists
if [ ! -f "$CERT_DIR/cert.pem" ] || [ ! -f "$CERT_DIR/key.pem" ]; then
    echo "Generating self-signed TLS certificate..."
    mkdir -p "$CERT_DIR"
    openssl req -x509 -newkey rsa:2048 \
        -keyout "$CERT_DIR/key.pem" \
        -out "$CERT_DIR/cert.pem" \
        -days 3650 -nodes \
        -subj '/CN=homeassistant' \
        -addext 'subjectAltName=DNS:homeassistant,DNS:*.ts.net,IP:127.0.0.1' \
        2>/dev/null
    echo "TLS certificate generated at $CERT_DIR/"
fi

echo "Redirect URI: $SPOTIFY_REDIRECT_URI"

streamlit run app/main.py \
    --server.port 8502 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.sslCertFile "$CERT_DIR/cert.pem" \
    --server.sslKeyFile "$CERT_DIR/key.pem" \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false
