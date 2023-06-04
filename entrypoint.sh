#!/bin/sh
# Set config
cat config/config_temp.yaml | envsubst > config/config.yaml
# Create tables
python3 init_db.py
exec "$@"