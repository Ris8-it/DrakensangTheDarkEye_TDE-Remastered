#!/bin/sh
# Ask Codex for ONE inventory icon. Usage: sh tools/art/gen_icon.sh <key> <prompt-file> <style-ref.png>   (EDIT=1: ref is the base to edit)
# Output: assets/armory_icons_v2/src/<key>.png (1024x1024, transparent). Prompt passed word for word.
# A per-key reference override can be put in assets/armory_icons_v2/prompts/<key>.ref. Carriage returns in arguments are stripped.
cd "$(dirname "$0")/../.." || exit 1
CODEX="${CODEX:-/c/Users/RC/.vscode/extensions/openai.chatgpt-26.1021.22027-win32-x64/bin/windows-x86_64/codex.exe}"   # set CODEX to your codex.exe
CR=$(printf '\r')
KEY=$(printf %s "$1" | tr -d "$CR"); PF=$(printf %s "$2" | tr -d "$CR"); REF=$(printf %s "$3" | tr -d "$CR")
PROMPT=$(cat "$PF")
OUT="assets/armory_icons_v2/src/$KEY.png"
[ -f "assets/armory_icons_v2/prompts/$KEY.ref" ] && REF=$(tr -d "$CR" < "assets/armory_icons_v2/prompts/$KEY.ref")
if [ -n "$EDIT" ]; then MODE="This is an EDIT: give the provided image to the image tool as the BASE IMAGE to edit (image edit mode). Keep the same object, composition, camera and lighting."; else MODE="Attach the provided image to the image tool as a STYLE REFERENCE ONLY: match its painting style, lighting direction, colour saturation and dark shading, not its subject."; fi
[ -n "$PROMPT" ] || { echo "empty prompt for $KEY"; exit 1; }
timeout 480 "$CODEX" exec -i "$REF" -s workspace-write --skip-git-repo-check -o "assets/armory_icons_v2/prompts/last-$KEY.txt" "Use your built-in image generation tool to create exactly ONE image with a TRANSPARENT background. Pass the text between the markers to the image tool WORD FOR WORD: do not rewrite, expand, shorten or add anything. $MODE Size: square 1024x1024.
Then save the generated PNG, keeping its alpha channel, to $OUT. Do not create or modify any other file. Reply with only the saved path.
---PROMPT START---
$PROMPT
---PROMPT END---" < /dev/null
ls -la "$OUT"
