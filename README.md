# Puppet Bolt Rundeck Node Executor and File Copier
This is a [Rundeck Node Executor Plugin](http://rundeck.org/docs/developer/node-executor-plugin.html) that provides remote command and script execution, and file transfers, on Rundeck using Puppet Bolt.


## Install
Download the plugin from the [Releases](https://github.com/ndelo/rundeck-puppet-bolt-node-executor/releases/tag/0.1) page.
Copy rundeck-puppet-bolt-node-executor.zip to the  libtext/ folder of $RUNDECK_BASE. 

## Features
The plugin supprts the following features:
- SSH using passwords or keys
- pseduo tty support
- WinRM over SSL or non-SSL transport
- Uses Rundeck keystorage for credentials and keys

## Node-level Properties
The following properties can be overwritten at the node-level:
- bolt-user
- bolt-protocol
- bolt-credential

Note: If no bolt-user is specified, then plugin will default to node's 'username' value.

## Bolt configuration files
No bolt specific configuration is needed. However, if you wish to use Bolt configuration files, these should exist in a .puppetlabs folder in the home directory of the rundeck user, usually $RUNDECK_BASE.

## Notes about this plugin

This plug has been developed and tested on the following:
- Bolt version 0.18.0
- Python version 2.7.5
- Oracle Enterprise Linux 7
