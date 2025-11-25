#!/usr/bin/env bash
set -e -o pipefail -o nounset -o errexit

python3 manage.py migrate

# load demo data
python3 manage.py load_demo_data
rm -rf staff/commands/*


# flag executable
cat >/tmp/flag.c << 'EOF'
#include <stdio.h>

#ifndef FLAG_VALUE
#define FLAG_VALUE "MISSING_FLAG"
#endif

int main(void) {
    puts(FLAG_VALUE);
    return 0;
}
EOF

gcc -O2 -DFLAG_VALUE=\""$FLAG_EXECUTABLE"\" /tmp/flag.c -o /read_flag
rm /tmp/flag.c

chown root:root /read_flag
chmod 711 /read_flag

# if the file /app/.do_not_destroy exists, do not destroy the container
if [ ! -f /app/.do_not_destroy ]; then
    echo "WILL DESTOY"
   echo "# $FLAG_APPFILE" >> /app/pycket/settings.py

   chmod -R 777 .

   # cleanup and actually run
   for var in "${!FLAG_@}"; do
      [[ $var == FLAG_ADMIN ]] || unset "$var"
   done
   rm -rf /app/meta/
fi
exec gosu 1000:1000 "$@"
