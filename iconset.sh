#!/bin/bash

# Create the iconset directory
mkdir -p src/icons/icon.iconset

# Create the iconset images
sips -z 16 16     src/icons/icon.png --out src/icons/icon.iconset/icon_16x16.png
sips -z 32 32     src/icons/icon.png --out src/icons/icon.iconset/icon_16x16@2x.png
sips -z 32 32     src/icons/icon.png --out src/icons/icon.iconset/icon_32x32.png
sips -z 64 64     src/icons/icon.png --out src/icons/icon.iconset/icon_32x32@2x.png
sips -z 128 128   src/icons/icon.png --out src/icons/icon.iconset/icon_128x128.png
sips -z 256 256   src/icons/icon.png --out src/icons/icon.iconset/icon_128x128@2x.png
sips -z 256 256   src/icons/icon.png --out src/icons/icon.iconset/icon_256x256.png
sips -z 512 512   src/icons/icon.png --out src/icons/icon.iconset/icon_256x256@2x.png
sips -z 512 512   src/icons/icon.png --out src/icons/icon.iconset/icon_512x512.png

# Create the iconset images for macOS
cp src/icons/icon.png src/icons/icon.iconset/icon_512x512@2x.png

# Convert the iconset to icns
iconutil -c icns -o src/icons/icon.icns src/icons/icon.iconset
