# Use the official PHP image with Apache
FROM php:8.1-apache

USER root

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Update php.ini to allow URL fopen and inclue
RUN echo "allow_url_fopen = On\nallow_url_include = On" >> /usr/local/etc/php/conf.d/docker-php-ext-allow-url-fopen.ini

# Copy your source files to the Apache document root
COPY . /var/www/html/

COPY meta/entrypoint.sh /entrypoint.sh

# Set the entrypoint script to run on container start
ENTRYPOINT ["/entrypoint.sh"]

# By default, start Apache in the foreground
CMD ["apache2-foreground"]

# Expose port 80 to access the application
EXPOSE 80