"""tiktok-dl Configuration Editor

As a command-line program, this script can be used to view and amend
tiktok-dl configuration files, either via arguments or via an
interactive prompt.

As a module, this script offers the functionality of the above whilst
allowing you to write your own scripts that work with tiktok-dl config
files.

This script requires the following modules in order to run:
- `argparse`

The idea behind the configuration script is to ensure that the same set
of rules are followed when downloading from any given user's page. For
example, you might want to ensure that no videos uploaded before a
certain date are downloaded, or you may want to ensure that you never
download one or two videos.

Format
------
Each user has their own configuration object within the root
configuration object. Within each user object, the following key-value
pairs can be stored:
ignore : list of str
	A list of links to always ignore when downloading from the user's
	page.
notbefore: str
	Videos uploaded before this date will never be downloaded from this
	user.
comment: str
	Let's you attach a note to a given user.
All of these objects are then put into a root object, and then saved in
the JSON format.

Accepted Input
--------------
For any arguments that aren't preceded by an option, they will be
treated as a username. After processing all of the command-line options,
the configuration objects belonging to the given users will be printed.
If the user doesn't have one, the user will be informed of this.

Command-Line Options
--------------------
--help
	Prints the module docstring then exits the program.
--version
	Prints the version number for this program.
--set username property value
	Updates the given user's `property` property with the given value.
	A user's configuration object will be created if it doesn't exist
	already. This will not change any `ignore` property. You can remove
	a property by setting a blank string with `""`.
--ignore link
	Adds the given link to the appropriate user's ignore property; if it
	isn't already ignored. If it is ignored, it is removed from the
	ignore list.
--delete username
	Deletes a given user's configuration object.
--list [filter]
	Lists all the users who have configuration objects after processing
	the other options. The optional filter is a regular expression that
	must fully match with a username before it can be displayed. Only
	the filter provided last will be used, if multiple `--list` options
	are given.
--config filepath
	Specifies the location of the configuration file to amend/query. If
	more than one is given, then the last one given will be used. If one
	is not specified, `./config.json` will be used.

Exports
-------
	* argument_parser - Constructs the tiktok-config argument parser.
	* load_or_create_config - Attempts to load a given configuration
		file.
"""

import sys
import os
import io
import copy
import argparse
from argparse import ArgumentParser
import tiktok_common as common

def argument_parser() -> ArgumentParser:
	"""Generates an argument parser for tiktok-config.
	
	Returns
	-------
	argparse.ArgumentParser
		The argument parser that is compatible with tiktok-config.
	"""
	
	parser = argparse.ArgumentParser( add_help=False, \
		description="Edits tiktok-dl configuration files.")
	parser.add_argument('-h', '--help', action='store_true')
	parser.add_argument('-v', '--version', action='version', \
		version=common.version_string())
	parser.add_argument('-s', '--set', action='append', nargs=3, \
		metavar=('USERNAME', 'PROPERTY', 'VALUE'))
	parser.add_argument('-i', '--ignore', action='append', \
		metavar='LINK')
	parser.add_argument('-d', '--delete', action='append', \
		metavar='USERNAME')
	parser.add_argument('-l', '--list', nargs='?', const='.*', \
		metavar='FILTER')
	parser.add_argument('-c', '--config', default='./config.json', \
		metavar='FILEPATH')
	parser.add_argument('--interactive', action='store_true')
	parser.add_argument('user', nargs='*', metavar='USERNAME')
	return parser

def load_or_create_config(filepath: os.path, \
	stream: io.TextIOBase = sys.stdout) -> dict:
	"""Loads a given UTF-8 configuration file and returns it, if it
	exists.
	
	This function attempts to load the configuration file. If it exists,
	it will be parsed and returned. If it doesn't exist, a message will
	be printed to the given text stream informing the user that a new
	configuration file will be created, and a blank configuration object
	is returned.
	
	Parameters
	----------
	filepath : os.path
		The path leading to the configuration file.
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	
	Returns
	-------
	dict
		The root JSON object containing all of the user objects.
	
	Raises
	------
	Any exception that can be raised by `open()` or `json.load()`,
	except `FileNotFoundError`, which is caught and handled as described
	above.
	"""
	
	try:
		return common.load_config(filepath)
	except FileNotFoundError:
		common.notice( \
			f"Will create new configuration script at \"{filepath}\".", stream)
		return {}

def perform_sets(config: dict, commands: list[tuple[str, str, str]], \
	stream: io.TextIOBase = sys.stdout) -> dict:
	"""Perform a bunch of set operations on a given config object.
	
	Parameters
	----------
	config - dict
		The configuration object to change. Note that the original
		object is not modified.
	commands - list of tuple of str, str, str
		The set operations to perform. The first string should contain
		the name of the user to perform the operation on. The second
		string should contain the property that is being amended. And
		the third string should contain the new value.
	stream - io.TextIOBase
		The stream to write messages to. Can be `None`. Defaults to
		`sys.stdout`.
	
	Returns
	-------
	dict
		The new configuration object, which is always a deep copy of the
		original.
	"""
	
	result = copy.deepcopy(config)
	for command in commands:
		# Clean up the usernames and property names.
		username = command[0].strip().lower()
		property = command[1].strip().lower()
		value = command[2]
		# Skip command if the property name is invalid.
		if property == "ignore":
			common.notice("Cannot use --set with the \"ignore\" property, " \
				f"use --ignore instead, in command: \"{command}\".", stream)
		elif property != "notbefore" and property != "comment":
			common.notice(f"Invalid property \"{property}\", in command: " \
				f"\"{command}\".", stream)
		else:
			# If this is a new user, inform the user.
			if username not in result:
				common.notice("Creating new configuration object for user " \
					f"\"{username}\".", stream)
				result[username] = {}
			# Perform set operation.
			if value == "":
				if property in result[username]:
					common.notice(f"Deleting property \"{property}\" from " \
						f"user \"{username}\".")
					result[username].pop(property, None)
			else:
				is_it_new = " "
				if property not in result[username]:
					is_it_new = " new "
				common.notice(f"Setting{is_it_new}property \"{property}\" " \
					f"to \"{value}\" for user \"{username}\".", stream)
				result[username][property] = value
	return result

if __name__ == "__main__":
	common.check_python_version()
	options = common.check_and_parse_arguments(argument_parser())
	
	if options.help:
		common.print_pages(common.create_pages(__doc__))
	else:
		config = load_or_create_config(options.config)
		new_config = perform_sets(config, options.set)
		print(config)
		print(new_config)