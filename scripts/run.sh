#!/bin/sh
mkdir -p "$XDG_RUNTIME_DIR"
exec "$SNAP/usr/bin/python3" "$SNAP/bin/mkvbatchmultiplex" "$@"
