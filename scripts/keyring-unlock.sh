#!/bin/bash

killall -q -u "$(whoami)" gnome-keyring-daemon
printf "M0z1ll4!" | gnome-keyring-daemon --daemonize --unlock
