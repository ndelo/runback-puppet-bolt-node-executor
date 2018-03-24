import os
import subprocess
import sys
import uuid
import yaml
import json

try:
	# bolt gems need a HOME env
	if not "HOME" in os.environ: 
		os.environ["HOME"] = os.getenv("RD_RUNDECK_BASE")
	
	# read in our bolt configuration file if one exists
	bolt_cfg_path = os.environ["HOME"] + '/.puppetlabs/bolt.yml'
	
	if os.path.exists(bolt_cfg_path):
		# create dictionary from config
		f = open(bolt_cfg_path, 'r')
		bolt_cfg = yaml.load(f)
		f.close()

	protocol = os.getenv("RD_CONFIG_PROTOCOL")
	node = protocol + "://" + (os.getenv("RD_NODE_NAME"))
	rd_exec_command = os.getenv("RD_EXEC_COMMAND") 

	COMMAND = ["/usr/local/bin/bolt", "command", "run", rd_exec_command, "-n", node, "-u"]

	if "RD_CONFIG_BOLT_USER" in os.environ:
		COMMAND.append(os.getenv("RD_CONFIG_BOLT_USER"))
	else:
		COMMAND.append(os.getenv("RD_NODE_USERNAME"))

	if protocol == "ssh":

		if "RD_CONFIG_USE_SSH_KEY" in os.environ:			

			if os.getenv("RD_CONFIG_CREDENTIAL"):
				# bolt requires that --private-key be the path to a keyfile
				# so we create a temp keyfile for use that is later cleaned up
				path = os.getenv("RD_RUNDECK_BASE") + "/.bolt"

				if not os.path.exists(path):
					os.makedirs(path)
				
				keypath = "%s/%s" % (path,str(uuid.uuid4()))
				privatekey = os.getenv("RD_CONFIG_CREDENTIAL")
				killkey = True
				
				f = open(keypath, 'w')
				f.write(privatekey)
				f.close()

			else:
				try:
					if "private-key" in bolt_cfg_path["ssh"]:
						keypath = bolt_cfg["ssh"]["private-key"]
				except:
					pass

			try: 
				keypath
			except NameError: 
				raise
			
			COMMAND.append("--private-key")
			COMMAND.append(os.path.expanduser(keypath))

		else:
			if not "RD_CONFIG_CREDENTIAL" in os.environ:
				raise Exception("Password missing")
			else:
				COMMAND.append("--password")
				COMMAND.append(os.getenv("RD_CONFIG_CREDENTIAL"))
		
		# enforce host key checking if set in bolt config
		try:
			if bolt_cfg["ssh"]["host-key-check"] == False:
				COMMAND.append("--no-host-key-check")
		except:
			COMMAND.append("--no-host-key-check")
		
		if os.getenv("RD_CONFIG_USE_TTY"):
			COMMAND.append("--tty")

	if protocol == "winrm":

		if "RD_CONFIG_USE_SSH_KEY" in os.environ:
			raise Exception('SSH keys cannot be used with the winrm protocol')

		if not os.getenv("RD_CONFIG_USE_WINRM_SSL"):
			COMMAND.append("--no-ssl")

		try:
			if bolt_cfg["winrm"]["ssl"] == False:
				COMMAND.append("--no-ssl")
			else:
				COMMAND.append("--ssl")
		except:
			pass
	
	# for debug we print out bolt debug info, as well as
	# rd environment variables and the full bolt command
	if os.getenv("RD_JOB_LOGLEVEL") == "DEBUG":
		COMMAND.append("--debug")

		arr_command = COMMAND[:]
		if "--password" in arr_command:
			arr_command[arr_command.index("--password") + 1] = "[SECURE]"
		
		str_command = ''
		for command in arr_command:
			str_command += command + ' '
		
		print 'Bolt command: ' + str_command.strip() + '\n'

		if os.path.exists(bolt_cfg_path):
			print 'Bolt Configuration File: ' + json.dumps(bolt_cfg) + '\n'

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
		if killkey == True:
			os.remove(keypath)
	except:
		pass