[Unit]
Description=VPN Admin Panel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_GROUP}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/.venv/bin"
ExecStart=${APP_DIR}/.venv/bin/gunicorn --bind ${BIND_ADDRESS}:${APP_PORT} run:app
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
