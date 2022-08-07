"""tiktok-dl Configuration Editor

As a command-line program, this script can be used to view and amend
tiktok-dl configuration files, either via arguments or via an
interactive prompt.

As a module, this script offers the functionality of the above whilst
allowing you to write your own scripts that work with tiktok-dl config
files.

This script requires the following modules in order to run:
- `argparse`
- `columnify`

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
--interactive
	Enters interactive mode. In this mode, the user will be prompted to
	enter a link. This will then be either added to or removed from the
	appropriate user's ignored links. Then, the prompts will loop
	infinitely, until the user shuts down the program.

Exports
-------
	* argument_parser - Constructs the tiktok-config argument parser.
	* load_or_create_config - Attempts to load a given configuration
		file.
	* perform_sets - Perform set operations on a config object.
	* perform_ignores - Add or remove links to/from a config object.
	* perform_deletes - Delete users from a config object.
	* list_users_with_config_objects - Lists users with a config object.
	* list_user_objects - Lists user config objects.
"""

import sys
import os
import io
import copy
import re
import argparse
from argparse import ArgumentParser
from columnify import columnify
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

def perform_ignores(config: dict, ignores: list[str], \
	stream: io.TextIOBase = sys.stdout) -> dict:
	"""Add and/or remove ignore links from a given config object.
	
	Parameters
	----------
	config - dict
		The configuration object to change. Note that the original
		object is not modified.
	ignores - list of str
		The links to ignore. If the link is already present, then remove
		it from its ignore property.
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
	for link in ignores:
		# Clean up the link and extract the username.
		# If the username cannot be extracted, it's an invalid link.
		link = link.strip().lower()
		if link.find('?') >= 0:
			link = link[:link.find('?')]
		if link != "" and link[-1] == '/':
			link = link[:-1]
		if link.find('@') < 0 or link.find('/') < 0:
			common.notice(f"Cannot extract username from link \"{link}\"; " \
				"the link is invalid.", stream)
		else:
			username = link[link.find('@') + 1:]
			username = username[:username.find('/')]
			# If this is a new user, inform the user.
			if username not in result:
				common.notice("Creating new configuration object for user " \
					f"\"{username}\".", stream)
				result[username] = {}
			if "ignore" not in result[username]:
				result[username]["ignore"] = []
			if link in result[username]["ignore"]:
				common.notice(f"Removing link \"{link}\" from user "
					f"\"{username}\"'s ignored links.", stream)
				result[username]["ignore"].remove(link)
			else:
				common.notice(f"Adding link \"{link}\" to user "
					f"\"{username}\"'s ignored links.", stream)
				result[username]["ignore"].append(link)
	return result

def perform_deletes(config: dict, usernames: list[str], \
	stream: io.TextIOBase = sys.stdout) -> dict:
	"""Delete user objects from a given config object.
	
	Parameters
	----------
	config - dict
		The configuration object to change. Note that the original
		object is not modified.
	usernames - list of str
		The users to delete.
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
	for username in usernames:
		# Clean up the username.
		username = username.strip().lower()
		# Delete the user if they exist.
		if username in result:
			common.notice(f"Deleting user \"{username}\"'s configuration " \
				"object", stream)
			result.pop(username, None)
		else:
			common.notice(f"Cannot delete user \"{username}\"; user does " \
				"not exist.", stream)
	return result

def list_users_with_config_objects(config: dict, filter_re: str = ".*", \
	stream: io.TextIOBase = sys.stdout) -> list[str]:
	"""List users who have a config object in a given config object.
	
	Parameters
	----------
	config - dict
		The configuration object to read from.
	filter - list of str
		The regular expression to filter the usernames with. The
		username must fully match to be included.  Defaults to listing
		all of the users who have objects.
	stream - io.TextIOBase
		The stream to write messages to. Can be `None`. Defaults to
		`sys.stdout`.
	
	Returns
	-------
	list of str
		The names of users who have a config object.
	"""
	
	try:
		reg = re.compile(filter_re)
	except re.error:
		common.notice("Invalid regular expression given for --list's " \
			f"filter: {filter_re}", stream)
		return []
	result = list(filter(reg.fullmatch, list(config.keys())))
	result.sort()
	return result

def list_user_objects(config: dict, users: list[str], \
	stream: io.TextIOBase = sys.stdout) -> list[str]:
	"""List the contents of user objects from a given config object.
	
	Parameters
	----------
	config - dict
		The configuration object to read from.
	users - list of str
		The users whose objects are to be listed.
	stream - io.TextIOBase
		The stream to write messages to. Can be `None`. Defaults to
		`sys.stdout`.
	
	Returns
	-------
	list of str
		The printable string representations of each user's config
		object, in the order that the users were originally given in.
	"""
	
	result = []
	for i, user in enumerate(users):
		if user in config:
			result.append(f"~~~{user}~~~\n")
			if "date" in config[user]:
				result[-1] += "No videos from before: " \
					f"{config[user]['date']}.\n"
			if "comment" in config[user]:
				result[-1] += f"Comment: {config[user]['comment']}\n"
			if "ignore" in config[user]:
				result[-1] += f"Ignoring {len(config[user]['ignore'])} " \
					"links.\n"
			if result[-1] == f"~~~{user}~~~\n":
				result[-1] += "Empty.\n"
		else:
			common.notice(f"User \"{user}\" does not exist; cannot list its " \
				"configuration object.", stream)
	result.sort()
	# Remove last newline.
	if len(result) > 0:
		result[-1] = result[-1][:-1]
	return result

if __name__ == "__main__":
	try:
		common.check_python_version()
		options = common.check_and_parse_arguments(argument_parser())
		
		if options.help:
			common.print_pages(common.create_pages(__doc__))
		else:
			config = load_or_create_config(options.config)
			if options.set is not None:
				config = perform_sets(config, options.set)
			if options.ignore is not None:
				config = perform_ignores(config, options.ignore)
			if options.delete is not None:
				config = perform_deletes(config, options.delete)
			# At this juncture, save the configuration.
			common.save_config(options.config, config)
			
			# Now process query stuff.
			if options.list is not None:
				username_list = \
					list_users_with_config_objects(config, options.list)
			else:
				username_list = []
			config_objects_to_print = list_user_objects(config, options.user)
			
			if len(username_list) > 0:
				print("")
				print(columnify(username_list, os.get_terminal_size().columns))
			if len(config_objects_to_print) > 0:
				print("")
				[print(user_obj) for user_obj in config_objects_to_print]
			
			# Enter interactive mode.
			if options.interactive:
				if len(username_list) > 0 or len(config_objects_to_print) > 0:
					print("")
				common.notice("Now entering interactive mode.")
				print("Input links, one at a time, that are to be ignored.")
				print("Each link will be saved as they are entered.")
				print("Issue Ctrl+C to shutdown interactive mode.\n")
				while True:
					link = input("> ")
					config = perform_ignores(config, [link])
					common.save_config(options.config, config)
	except KeyboardInterrupt:
		common.notice("Exiting...")