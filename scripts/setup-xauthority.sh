# shellcheck shell=bash

export DISPLAY="${DISPLAY:-:0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

find_xauthority() {
  for candidate in \
    "${XDG_RUNTIME_DIR}/gdm/Xauthority" \
    "${XDG_RUNTIME_DIR}"/.mutter-Xwaylandauth.* \
    "${HOME}/.Xauthority"; do
    if [ -r "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
}

source_xauthority="${XAUTHORITY:-$(find_xauthority)}"
if [ -n "$source_xauthority" ]; then
  export XAUTHORITY="$source_xauthority"
fi

if [ -n "${XAUTHORITY:-}" ] && command -v xauth >/dev/null 2>&1; then
  case "$-" in
    *x*) restore_xtrace=1 ;;
    *) restore_xtrace=0 ;;
  esac

  set +x
  xauth_cookie="$(xauth -f "$XAUTHORITY" list 2>/dev/null | awk '/MIT-MAGIC-COOKIE-1/ { print $3; exit }')"
  if [ -n "$xauth_cookie" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
    touch "$XAUTHORITY"
    chmod 600 "$XAUTHORITY"
    xauth -f "$XAUTHORITY" add "$(hostname)/unix:0" MIT-MAGIC-COOKIE-1 "$xauth_cookie"
  fi
  unset xauth_cookie

  if [ "$restore_xtrace" = "1" ]; then
    set -x
  fi
fi

echo "DISPLAY=${DISPLAY:-}"
echo "XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-}"
echo "SOURCE_XAUTHORITY=${source_xauthority:-}"
echo "XAUTHORITY=${XAUTHORITY:-}"

if [ -n "${XAUTHORITY:-}" ]; then
  ls -l "$XAUTHORITY" || true
  xauth -f "$XAUTHORITY" list 2>&1 | sed -E 's/[0-9a-fA-F]{32,}/<redacted>/g' || true
fi
