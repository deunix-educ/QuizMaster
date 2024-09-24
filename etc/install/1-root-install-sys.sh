#!/bin/bash
if [ $EUID -ne 0 ]; then
  echo "Lancer en root: # $0" 1>&2
  exit 1
fi

INSTALL_SQLITE3="true"
INSTALL_POSTGRES="false"
INSTALL_MARIADB="false"

apt update
#apt upgrade

apt install build-essential binutils supervisor mosquitto
if  [ "$INSTALL_SQLITE3" == "true" ]; then
apt install sqlite3
fi
if  [ "$INSTALL_POSTGRES" == "true" ]; then
apt install postgresql postgresql-contrib libpq-dev
fi
if  [ "$INSTALL_MARIADB" == "true" ]; then
apt install mariadb-server mariadb-client default-libmysqlclient-dev
fi

apt install python3-dev python3-pip python3-venv

# supervisor http access
if [ ! -e "/etc/supervisor/supervisord.conf.old" ]; then
cp /etc/supervisor/supervisord.conf /etc/supervisor/supervisord.conf.old

cat >> /etc/supervisor/supervisord.conf << EOF
[inet_http_server]
port = 9001
username = root
password = toor
EOF
fi

apt install ssl-cert
echo "--- generate dhparam.pem"
openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

