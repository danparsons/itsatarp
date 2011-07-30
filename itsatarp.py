#!/usr/bin/python

# This script was written as a simple replacement for snmptt. It takes input from
# snmptrapd, parses the source IP from it, and then searches nagios config files
# for the IP. It looks for it under "__mgmt_ip" first, and if it doesn't find it
# there, it looks for it under "address". Once it finds a match, it obtains the
# hostname associated with the IP and submits a passive service check to Nagios.

import os
import sys
import re
import time
import syslog

NAGIOS_SERVICE_NAME="snmptrap"

NAGIOS_CONFIG_DIR="/home/nagios/nagios/etc"
NAGIOS_COMMAND_FILE="/home/nagios/nagios/var/rw/nagios.cmd"

def getRealHost(ip):
	host_regex = re.compile(r'define.host.{')
	mgmt_regex = re.compile(r'__mgmt_ip\s*(\S*)')
	hostname_regex = re.compile(r'host_name\s*(\S*)')
	address_regex = re.compile(r'address\s*(\S*)')
	for root, dirs, files in os.walk(NAGIOS_CONFIG_DIR):
		for x in files:
			theFile = os.path.join(root, x)
			if os.path.splitext(theFile)[1] == ".cfg":
				fp = open(theFile, 'r')
				someCfg = fp.read()
				fp.close()
				for host in host_regex.split(someCfg):
					mgmt_ip = mgmt_regex.search(host)
					address_ip = address_regex.search(host)
					hostname = hostname_regex.search(host)
					if hostname:
						if mgmt_ip:
							if mgmt_ip.group(1) == ip:
								return hostname.group(1)
						if address_ip:
							if address_ip.group(1) == ip:
								return hostname.group(1)
	return None
	
def submitPassiveCheck(host):
	msg = "[%s] PROCESS_SERVICE_CHECK_RESULT;%s;%s;%s;TRAP\n" % (int(time.time()), host, NAGIOS_SERVICE_NAME, "2")
	if (os.path.exists(NAGIOS_COMMAND_FILE)):
		cmdf = open(NAGIOS_COMMAND_FILE, "a")
		print "Submitting the following message to Nagios: %s" % msg
		syslog.syslog("itsatarp.py: Submitting passive check to Nagios: %s" % msg)
		cmdf.write(msg)
		cmdf.close()
	else:
		print "ERROR: Command file %s doesn't exist; exiting." % NAGIOS_COMMAND_FILE
		return -2
	
def main():
	ip_regex = re.compile(r'UDP:\s*\[(.*?)\]')
	trap = sys.stdin.read()
	ip = ip_regex.search(trap)
	if ip:
		#print "IP found: %s" % ip.group(1)
		host = getRealHost(ip.group(1))
		submitPassiveCheck(host)
	else:
		print "No IP found"
		sys.exit(1)
		

if __name__ == '__main__':
	main()
