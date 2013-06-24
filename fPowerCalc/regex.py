# import re

# a="192.168.1."
# ValidIpAddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
# port
# m=re.compile(ValidIpAddressRegex)

# t = m.match(a)

# if t is not None:
# 	print "t is not non"



print "Please enter port: "
port = raw_input()

try:
	port = int(port)
	print "INT"

except:
	print "port is not an int"

	