#!/usr/bin/env bash
set -euo pipefail

if ! command -v nginx >/dev/null 2>&1; then
    printf '[10-nginx] nginx not installed, skipping.\n'
    exit 0
fi

APP_DIR="${APP_DIR:-/opt/vpn-admin}"
TEMPLATE_PATH="${APP_DIR}/scripts/templates/nginx.conf.tpl"
SITE_AVAILABLE="/etc/nginx/sites-available/vpn-admin"
SITE_ENABLED="/etc/nginx/sites-enabled/vpn-admin"

if [[ ! -f "$TEMPLATE_PATH" ]]; then
    printf '[10-nginx] Template %s not found, skipping.\n' "$TEMPLATE_PATH"
    exit 0
fi

SERVER_NAME="${DOMAIN:-${SERVER_NAME:-_}}"
APP_PORT="${APP_PORT:-55151}"

export SERVER_NAME APP_PORT

mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled

printf '[10-nginx] Rendering nginx vhost for %s (port %s).\n' "$SERVER_NAME" "$APP_PORT"
envsubst '${SERVER_NAME} ${APP_PORT}' <"$TEMPLATE_PATH" >"$SITE_AVAILABLE"

ln -sf "$SITE_AVAILABLE" "$SITE_ENABLED"

if [[ -e /etc/nginx/sites-enabled/default ]]; then
    rm -f /etc/nginx/sites-enabled/default
fi

nginx -t
systemctl restart nginx
