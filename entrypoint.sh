#!/bin/bash
set -e

# Auto-install TinyMCE if not present
TINYMCE_DIR="app/static/tinymce"
if [ ! -f "$TINYMCE_DIR/tinymce.min.js" ]; then
    echo "Installing TinyMCE 6.8.2..."
    mkdir -p "$TINYMCE_DIR"
    curl -sL "https://download.tiny.cloud/tinymce/community/tinymce_6.8.2.zip" -o /tmp/tinymce.zip
    unzip -qo /tmp/tinymce.zip -d /tmp/tinymce_extract
    cp -r /tmp/tinymce_extract/tinymce/js/tinymce/* "$TINYMCE_DIR/"
    rm -rf /tmp/tinymce.zip /tmp/tinymce_extract
    echo "TinyMCE installed to $TINYMCE_DIR/"
else
    echo "TinyMCE already installed."
fi

# Start the application
exec "$@"
