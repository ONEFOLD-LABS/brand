#!/usr/bin/env sh
# Rebuild everything in logos/ and tokens/tokens.css.
# Needs: python3 with fonttools, rsvg-convert (librsvg), curl.
set -eu
cd "$(dirname "$0")/.."
FONTS=.fonts
if [ ! -f "$FONTS/Archivo[wdth,wght].ttf" ]; then
  mkdir -p "$FONTS"
  curl -sSfL -o "$FONTS/Archivo[wdth,wght].ttf" \
    "https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth,wght%5D.ttf"
fi
python3 tools/make_logo.py --fonts "$FONTS" --out logos
rsvg-convert -w 1024 -h 1024 logos/onefold-mark.svg -o logos/onefold-mark-1024.png
rsvg-convert -w 1024 -h 1024 logos/onefold-avatar.svg -o logos/onefold-avatar-1024.png
rsvg-convert -w 1024 logos/onefold-lockup.svg -o logos/onefold-lockup-1024.png
python3 tools/tokens_css.py tokens/tokens.json > tokens/tokens.css
echo "done"
