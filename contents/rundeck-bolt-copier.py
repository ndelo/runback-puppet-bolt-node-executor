import os
import subprocess
import sys
import uuid
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('source')
parser.add_argument('destination')
args = parser.parse_args()


try:
	print args.destination

	if not "RD_CONFIG_CREDENTIAL" in os.environ:
		raise Exception('No bolt credentials set')

	# bolt gems need a HOME env variable
	if not "HOME" in os.environ:
		os.environ["HOME"] = os.getenv("RD_RUNDECK_BASE")

	protocol = os.getenv("RD_CONFIG_PROTOCOL")
	node = protocol + "://" + (os.getenv("RD_NODE_NAME"))
	exec_command = os.getenv("RD_EXEC_COMMAND") 

	COMMAND = ["/usr/local/bin/bolt", "file", "upload", "-n", node, args.source, args.destination, "-u"]
	if "RD_CONFIG_BOLT_USER" in os.environ:
		COMMAND.append(os.getenv("RD_CONFIG_BOLT_USER"))
	else:
		COMMAND.append(os.getenv("RD_NODE_USERNAME"))
		
	if "RD_CONFIG_USE_SSH_KEY" in os.environ:
		if protocol == 'winrm':
			raise Exception('SSH keys cannot be used with the winrm protocol')
		else:
			COMMAND.append("--private-key")

			path = os.getenv("RD_RUNDECK_BASE") + "/.bolt"

			if not os.path.exists(path):
				os.makedirs(path)

			keypath = "%s/%s" % (path,str(uuid.uuid4()))
			privatekey = os.getenv("RD_CONFIG_CREDENTIAL")

			f = open(keypath, 'w')
			f.write(privatekey)
			f.close()

			COMMAND.append(keypath)
			COMMAND.append("--no-host-key-check")
	else:
		COMMAND.append("--password")
		COMMAND.append(os.getenv("RD_CONFIG_CREDENTIAL"))

	if protocol == "ssh":
		if os.getenv("RD_CONFIG_USE_TTY"):
			COMMAND.append("--tty")
	else:
		if os.getenv("RD_CONFIG_WINRM_SSL"):
			COMMAND.append("--ssl")
		else:
			COMMAND.append("--no-ssl")

	if os.getenv("RD_JOB_LOGLEVEL") == "DEBUG":
		COMMAND.append("--debug")
		
		arr_command = COMMAND[:]
		if "--password" in arr_command:
			arr_command[arr_command.index("--password") + 1] = "[SECURE]"
		
		str_command = ''
		for command in arr_command:
			str_command += command + ' '
		
		print 'Bolt command:'
		print str_command.strip() + '\n'
		
		
		print 'RD Enviroment Variables'
		print '-----------------------'
		for var in os.environ:
			if var == 'RD_CONFIG_CREDENTIAL':
				print "%s=[SECURE]" % var
			else:
				print "%s=%s" % (var, os.getenv(var)) 

	output = subprocess.call(COMMAND)
	sys.exit(output)

except OSError as error:
	print >> sys.stderr, "Bolt encountered an error during execution:", error
	sys.exit(1)

finally:
	try:
		os.remove(keypath)
	except:
		pass