#!/usr/bin/env bash
set -euo pipefail

# Installed at /opt/dsai/deploy.sh and bound to the CI deploy key as an SSH
# forced command (authorized_keys: command="/opt/dsai/deploy.sh",restrict ...).
# The key can run only this script. The image tag arrives as the "ssh command"
# and sshd hands it over in SSH_ORIGINAL_COMMAND instead of executing it.
TAG="${SSH_ORIGINAL_COMMAND:-}"
if [ -z "$TAG" ]; then
  echo "Usage: ssh -i <deploy key> deploy@host '<image-tag>'" >&2
  exit 1
fi
# The CI key can reach this script, so the tag is re-checked here; it goes into
# a sed expression below.
if ! [[ "$TAG" =~ ^[A-Za-z0-9._-]{1,128}$ ]]; then
  echo "Refusing tag '$TAG', unexpected characters." >&2
  exit 1
fi

cd /opt/dsai
COMPOSE=(docker compose -f docker-compose.prod.yml)

# active_slot is written only after a successful cutover, so a crash mid-deploy
# always leaves it naming whatever is really still live.
ACTIVE_SLOT_FILE=active_slot
if [ ! -f "$ACTIVE_SLOT_FILE" ]; then
  echo "No ${ACTIVE_SLOT_FILE}: the one-time bootstrap has not run." >&2
  exit 1
fi
CURRENT=$(cat "$ACTIVE_SLOT_FILE")
case "$CURRENT" in
  blue) TARGET=green ;;
  green) TARGET=blue ;;
  *)
    echo "Corrupt ${ACTIVE_SLOT_FILE}: '${CURRENT}' (expected blue or green)." >&2
    exit 1
    ;;
esac

sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${TAG}/" .env

echo "Active slot is ${CURRENT}. Starting ${TARGET} on tag ${TAG} next to it..."
"${COMPOSE[@]}" pull "dsai-${TARGET}"
"${COMPOSE[@]}" up -d "dsai-${TARGET}"

# Streamlit's /_stcore/health answers "ok" as soon as the server is up. Neither
# slot publishes a port, so the probe runs inside the container's own network
# namespace (the image ships curl for its HEALTHCHECK). Three consecutive
# successes, 4 s apart, so a single early answer during startup cannot pass.
REQUIRED_CONSECUTIVE=3
CID=$("${COMPOSE[@]}" ps -q "dsai-${TARGET}")
READY=0
CONSECUTIVE=0
for i in $(seq 1 30); do
  if docker exec "$CID" curl -fsS http://127.0.0.1:8080/_stcore/health >/dev/null 2>&1; then
    CONSECUTIVE=$((CONSECUTIVE + 1))
    echo "[$i/30] dsai-${TARGET} healthy (${CONSECUTIVE}/${REQUIRED_CONSECUTIVE} consecutive)"
    if [ "$CONSECUTIVE" -ge "$REQUIRED_CONSECUTIVE" ]; then
      READY=1
      break
    fi
  else
    CONSECUTIVE=0
    echo "[$i/30] dsai-${TARGET} not healthy yet"
  fi
  sleep 4
done

if [ "$READY" -ne 1 ]; then
  echo "dsai-${TARGET} never became healthy on tag ${TAG}. ${CURRENT} keeps all traffic. Cleaning up ${TARGET}:" >&2
  "${COMPOSE[@]}" logs --tail 50 "dsai-${TARGET}" >&2
  "${COMPOSE[@]}" stop "dsai-${TARGET}"
  "${COMPOSE[@]}" rm -f "dsai-${TARGET}"
  exit 1
fi

echo "dsai-${TARGET} is ready. Flipping Caddy's upstream from ${CURRENT} to ${TARGET}..."
# The Caddyfile belongs to the portfolio stack (one shared edge for the box).
# Written with `>` (same inode), never `sed -i`: the file is bind-mounted into
# the caddy container and `sed -i` orphans that mount, see /opt/caddy-reload.sh.
CADDYFILE=/opt/portfolio/Caddyfile
if ! grep -qE "reverse_proxy dsai-(blue|green):8080" "$CADDYFILE"; then
  echo "Caddyfile has no dsai-blue/green upstream line to flip. Aborting before touching anything." >&2
  "${COMPOSE[@]}" stop "dsai-${TARGET}"
  "${COMPOSE[@]}" rm -f "dsai-${TARGET}"
  exit 1
fi
NEW_CADDYFILE=$(sed -E "s/reverse_proxy dsai-(blue|green):8080/reverse_proxy dsai-${TARGET}:8080/" "$CADDYFILE")
printf '%s\n' "$NEW_CADDYFILE" > "$CADDYFILE"

if ! /opt/caddy-reload.sh; then
  echo "Caddy rejected the new config. Reverting the upstream line, ${CURRENT} stays live." >&2
  REVERTED_CADDYFILE=$(sed -E "s/reverse_proxy dsai-(blue|green):8080/reverse_proxy dsai-${CURRENT}:8080/" "$CADDYFILE")
  printf '%s\n' "$REVERTED_CADDYFILE" > "$CADDYFILE"
  "${COMPOSE[@]}" stop "dsai-${TARGET}"
  "${COMPOSE[@]}" rm -f "dsai-${TARGET}"
  exit 1
fi

echo "$TARGET" > "$ACTIVE_SLOT_FILE"
echo "Cutover done. Removing old slot ${CURRENT}..."
"${COMPOSE[@]}" stop "dsai-${CURRENT}" || true
"${COMPOSE[@]}" rm -f "dsai-${CURRENT}" || true

echo "Deploy of tag ${TAG} complete. Active slot: ${TARGET}."
