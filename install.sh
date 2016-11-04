#!/bin/bash

if [[ $(id -u) != 0 ]]; then
	echo 'Please run this script as root!'
	exit 1
fi

echo 'Cloning github.com/danger-noodles/alarmpi...'
if cd /tmp/alarmpi; then
	git fetch -q; git reset --hard -q origin/master
else
	git clone -q git://github.com/danger-noodles/alarmpi /tmp/alarmpi
	cd $name
fi

echo 'Installing alarmpi script to $PATH...'
install -Dm755 /tmp/alarmpi/main.py /usr/bin/alarmpi

echo 'Installing alarmpi systemd service file...'
install -Dm644 /tmp/alarmpi/main.service /lib/systemd/system/alarmpi.service

echo 'Enabling alarmpi systemd service file...'
systemctl enable alarmpi.service
