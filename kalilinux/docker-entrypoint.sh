#!/usr/bin/env bash
set -e

if [ -z "$ROOT_PASSWORD" ]; then
    echo "WARNING: ROOT_PASSWORD not set, exiting..."
    exit
fi
echo "root:${ROOT_PASSWORD}" | chpasswd

exec "$@"
