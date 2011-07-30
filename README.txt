BACKGROUND
==========
This tool was created as a way to add quick and dirty SNMP trap receiving to Nagios
without having to muck around with MIB files for every device you're monitoring.

It has the advantage of supporting every device ever created that can send SNMP
traps.

It has the disadvantage of not passing any information on to Nagios except that a
trap was received. You won't know why a trap was sent unless you ask the device
that sent it.

This is perfect for situations where, say, a server's IPMI card won't
send a trap unless there's a hardware failure, and you want to hear about all
hardware failures.

It's not perfect in situations where you have a device that sends SNMP traps for
any event, even unimportant things like "I just synced my clock to a NTP server".

In the typical snmptrapd / Nagios flow, it serves as a simple replacement for snmptt. 
It takes input from snmptrapd, parses the source IP from it, and then recursively 
searches for the IP in "define host" blocks, in *.cfg, in a directory of Nagios config 
files. It looks first for the IP under "__mgmt_ip", and if it doesn't find it there, 
it looks for it under "address". Once it finds a match, it obtains the hostname 
from the "define host" block the IP was found in and then submits a passive service 
check result to Nagios.

The reason it looks for "__mgmt_ip" in addition to "address" is because I wanted to 
support servers that have two important IP addresses: one for the IPMI management 
card, and the other for the server OS itself. Either IP might send a trap, but in
Nagios I monitor IPMI-enabled system as a single host.

SETUP
=====
(1) Copy itsatarp.py somewhere. I store it in my Nagios libexec directory.

(2) Add the following to your snmptrapd.conf file:
traphandle default /home/nagios/nagios/libexec/itsatarp.py
disableAuthorization yes

(3) Edit NAGIOS_CONFIG_DIR and NAGIOS_COMMAND_FILE in itsatarp.py

(4) For all the hosts in Nagios that you want to receive traps from, be sure to add a 
passive service called "snmptrap". You can do this on a host-by-host basis or via 
templates in Nagios. Here's an example:

define service {
	name					snmptrap
	service_description 	snmptrap
	use						generic-service
	active_checks_enabled	0
	passive_checks_enabled	1
	contact_groups		admins
}