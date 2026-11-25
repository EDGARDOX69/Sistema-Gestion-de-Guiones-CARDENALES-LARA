#!/usr/bin/env bash
# MySQL/MariaDB local para pruebas y demo, sin sudo y sin tocar XAMPP.
#
# Usa los binarios de XAMPP (/Applications/XAMPP/xamppfiles) con un data dir
# propio en ~/.itinerario-mysql. El usuario root no tiene contraseña y solo
# escucha en 127.0.0.1:3306, igual que espera app/config.py.
#
# Uso:
#   scripts/expo/mysql_local.sh start|stop|status|init
set -euo pipefail

XAMPP=/Applications/XAMPP/xamppfiles
DATADIR="${ITINERARIO_MYSQL_DIR:-$HOME/.itinerario-mysql}"
CNF="$DATADIR/my.cnf"

case "${1:-status}" in
  init)
    rm -rf "$DATADIR"
    mkdir -p "$DATADIR"
    cat > "$CNF" <<EOF
[mysqld]
basedir=$XAMPP
datadir=$DATADIR
user=$(whoami)
port=3306
bind-address=127.0.0.1
socket=$DATADIR/mysql.sock
pid-file=$DATADIR/mysqld.pid
log-error=$DATADIR/error.log
innodb_flush_method=fsync
EOF
    "$XAMPP/bin/mariadb-install-db" --defaults-file="$CNF" \
      --auth-root-authentication-method=normal --skip-test-db
    ;;
  start)
    if nc -z 127.0.0.1 3306 2>/dev/null; then
      echo "MySQL ya responde en 127.0.0.1:3306"
      exit 0
    fi
    [[ -f "$CNF" ]] || { echo "Falta $CNF. Ejecuta: $0 init"; exit 1; }
    nohup "$XAMPP/sbin/mariadbd" --defaults-file="$CNF" >/dev/null 2>&1 &
    for _ in $(seq 1 30); do
      nc -z 127.0.0.1 3306 2>/dev/null && { echo "MySQL arriba en 127.0.0.1:3306"; exit 0; }
      sleep 1
    done
    echo "MySQL no arrancó. Revisa $DATADIR/error.log" >&2
    exit 1
    ;;
  stop)
    "$XAMPP/bin/mysqladmin" -h 127.0.0.1 -P 3306 -u root shutdown 2>/dev/null || true
    echo "MySQL detenido"
    ;;
  status)
    nc -z 127.0.0.1 3306 2>/dev/null && echo "MySQL arriba en 127.0.0.1:3306" \
      || echo "MySQL detenido"
    ;;
  *)
    echo "Uso: $0 start|stop|status|init" >&2
    exit 2
    ;;
esac
