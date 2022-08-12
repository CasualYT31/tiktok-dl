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
	Prints the version number for this program, then exits.
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
	* ConfigError - Exception thrown when loading config failed.
	* argument_parser - Constructs the tiktok-config argument parser.
	* load_or_create_config - Attempts to load a given config file.
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
import traceback
import argparse
from argparse import ArgumentParser
from columnify import columnify
import tiktok_common as common
from tiktok_common import IgnoreError, UserConfig

class ConfigError(Exception):
	"""Raised when an invalid configuration script was loaded."""
	pass

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
		metavar='CONFIGPATH')
	parser.add_argument('--interactive', action='store_true')
	parser.add_argument('user', nargs='*', metavar='USERNAME')
	return parser

def load_or_create_config(filepath: os.path, \
	stream: io.TextIOBase = sys.stdout) -> UserConfig:
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
	UserConfig
		The object containing all of the user objects.
	
	Raises
	------
	Any exception that can be raised by `UserConfig.load_config()`,
	except `FileNotFoundError`, which is caught and handled as described
	above.
	ConfigError
		If the given script was valid JSON, but an invalid tiktok-dl
		configuration file. This exception is raised from `TypeError`,
		`KeyError`, and `ValueError`.
	"""
	
	response = UserConfig()
	try:
		response.load_config(filepath)
	except FileNotFoundError:
		common.notice( \
			f"Will create new configuration script at \"{filepath}\".", stream)
	except KeyError as err:
		common.notice( \
			f"The given configuration file \"{filepath}\" was invalid. "
			f"Key did not exist in a user object: \"{err.args[0]}\".", stream)
		raise ConfigError from err
	except ValueError as err:
		common.notice( \
			f"The given configuration file \"{filepath}\" was invalid. "
			f"A value had an incorrect format.", stream)
		raise ConfigError from err
	except Exception as err:
		common.notice( \
			f"The given configuration file \"{filepath}\" was invalid. "
			"Cause:", stream)
		common.notice(traceback.format_exc(), stream)
		raise ConfigError from err
	return response

def perform_sets(config: UserConfig, commands: list[tuple[str, str, str]], \
	stream: io.TextIOBase = sys.stdout) -> UserConfig:
	"""Perform a bunch of set operations on a given config object.
	
	Parameters
	----------
	config - UserConfig
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
	UserConfig
		The new configuration object, which is always a deep copy of the
		original.
	"""
	
	result = copy.deepcopy(config)
	for command in commands:
		username = command[0]
		property = command[1]
		value = command[2]
		try:
			new_user = result.set(property, username, value)
			if new_user != "":
				common.notice("Created new configuration object for user " \
					f"\"{username}\".", stream)
		except AttributeError:
			common.notice(f"Invalid property \"{property}\", in command: " \
				f"\"{command}\".", stream)
		except IgnoreError:
			common.notice("Cannot use --set with the \"ignore\" property, " \
				f"use --ignore instead, in command: \"{command}\".", stream)
		except ValueError:
			common.notice(f"The value \"{value}\" did not have the correct " \
				f"format, in command: \"{command}\".", stream)
	return result

def perform_ignores(config: UserConfig, ignores: list[str], \
	stream: io.TextIOBase = sys.stdout) -> UserConfig:
	"""Add and/or remove ignore links from a given config object.
	
	Parameters
	----------
	config - UserConfig
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
	UserConfig
		The new configuration object, which is always a deep copy of the
		original.
	"""
	
	result = copy.deepcopy(config)
	for link in ignores:
		try:
			if result.toggle_ignore_link(link):
				common.notice(f"Added link \"{link}\" to user " \
					f"\"{common.extract_username_from_link(link)}\"'s " \
					"ignored links.", stream)
			else:
				common.notice(f"Removed link \"{link}\" from user " \
					f"\"{common.extract_username_from_link(link)}\"'s " \
					"ignored links.", stream)
		except ValueError:
			common.notice(f"The link \"{link}\" was invalid.", stream)
	return result

def perform_deletes(config: UserConfig, usernames: list[str], \
	stream: io.TextIOBase = sys.stdout) -> UserConfig:
	"""Delete user objects from a given config object.
	
	Parameters
	----------
	config - UserConfig
		The configuration object to change. Note that the original
		object is not modified.
	usernames - list of str
		The users to delete.
	stream - io.TextIOBase
		The stream to write messages to. Can be `None`. Defaults to
		`sys.stdout`.
	
	Returns
	-------
	UserConfig
		The new configuration object, which is always a deep copy of the
		original.
	"""
	
	result = copy.deepcopy(config)
	for username in usernames:
		try:
			result.delete_user(username)
			common.notice(f"Deleted user \"{username}\"'s configuration " \
				"object.", stream)
		except KeyError:
			common.notice(f"Could not delete user \"{username}\"; user does " \
				"not exist.", stream)
	return result

def list_users_with_config_objects(config: UserConfig, filter_re: str=".*", \
	stream: io.TextIOBase = sys.stdout) -> list[str]:
	"""List users who have a config object in a given config object.
	
	Parameters
	----------
	config - UserConfig
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
		return config.list_users(filter_re)
	except re.error:
		common.notice("Invalid regular expression given for --list's " \
			f"filter: {filter_re}", stream)
		return []

def list_user_objects(config: UserConfig, users: list[str], \
	stream: io.TextIOBase = sys.stdout) -> list[str]:
	"""List the contents of user objects from a given config object.
	
	Parameters
	----------
	config - UserConfig
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
		object, in ascending order.
	"""
	
	result = []
	for user in users:
		try:
			result.append(config.user_to_string(user))
		except KeyError:
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
			config.save_config(options.config)
			
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
					config.save_config(options.config)
	except (KeyboardInterrupt, ConfigError):
		common.notice("Exiting...")