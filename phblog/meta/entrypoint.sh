#!/usr/bin/env bash
set -e -o pipefail -o nounset -o errexit

#whoami
#hostname $FLAG_HOSTNAME

groupadd -r $FLAG_USERNAME
useradd -r -g $FLAG_USERNAME $FLAG_USERNAME

sed -i "s/www-data/$FLAG_USERNAME/g" /etc/apache2/apache2.conf
sed -i "s/www-data/$FLAG_USERNAME/g" /etc/apache2/envvars


# variable substitution
( echo "cat <<EOF" ; cat meta/000-default.conf ; echo EOF ) | sh > /etc/apache2/sites-available/000-default.conf

echo $FLAG_SECRETFILE >> /var/www/html/posts/secret-post.post

echo "admin,$FLAG_ADMINPASS" > /var/www/html/admin/credentials.txt

cp -r /var/www/html /var/www/$FLAG_DIR/
chown -R $FLAG_USERNAME:$FLAG_USERNAME /var/www/

echo $FLAG_ROOTFILE > /flag.txt

rm -rf /var/www/$FLAG_DIR/meta/

unset ${!FLAG_*}

exec "$@"
