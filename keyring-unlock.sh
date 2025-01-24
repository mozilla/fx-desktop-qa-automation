killall -q -u "$(whoami)" gnome-keyring-daemon
eval "$(printf 'M0z1ll4!' \
           | gnome-keyring-daemon --daemonize --login \
           | sed -e 's/^/export /')"
