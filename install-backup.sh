#!/bin/bash

backup_zip=$1
database_backup=$2
sql_password=$3
joomla_password=$4

sudo rm -rf /var/www/html
sudo unzip $backup_zip -d /var/www

cat << EOF > create_joomla_user.sql
CREATE DATABASE joomladb;
CREATE USER joomlauser@localhost;
SET PASSWORD FOR 'joomlauser'@'localhost' = PASSWORD("$4");
GRANT ALL PRIVILEGES ON joomladb.* TO 'joomlauser'@'localhost' IDENTIFIED BY '$4' WITH GRANT OPTION;
FLUSH PRIVILEGES;
quit
EOF

mysql -u root -p$3 < create_joomla_user.sql

sed -i '1s/^/USE joomladb;\n/' $2

mysql -u root -p$3 < $2

sudo a2enmod rewrite
rm /etc/apache2/sites-available/joomla.conf
rm /etc/apache2/sites-enabled/joomla.conf

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
ln -s /etc/apache2/sites-available/joomla.conf /etc/apache2/sites-enabled/joomla.conf

sudo systemctl restart apache2.service
