#!/bin/bash

backup_zip=$1

rm -rf /var/www/html
unzip $backup_zip -d /var/www

sudo a2enmod rewrite
rm /etc/apache2/sites-available/joomla.conf
rm /etc/apache2/sites-enabled/joomla.conf
touch /etc/apache2/sites-available/joomla.conf
ln -s /etc/apache2/sites-available/joomla.conf /etc/apache2/sites-enabled/joomla.conf

public_hostname=$(curl http://169.254.169.254/latest/meta-data/public-hostname)

cat << EOF > /etc/apache2/sites-available/joomla.conf
<VirtualHost *:80>
ServerAdmin info@rscds-youth.org
DocumentRoot /var/www/html/
ServerName $public_hostname
<Directory /var/www/html/>
Options FollowSymLinks
AllowOverride All
Order allow,deny
allow from all
</Directory>
ErrorLog /var/log/apache2/rscds-youth-test-site-error_log
CustomLog /var/log/apache2/rscds-youth-test-site-access_log common
</VirtualHost>
EOF

systemctl restart apache2.service
