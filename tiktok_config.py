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
	already.
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

Exports
-------
	* argument_parser - Constructs the tiktok-config argument parser.
"""

import sys
import argparse
import tiktok_common as common

def argument_parser():
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
	parser.add_argument('user', nargs='*', metavar='USERNAME')
	return parser

if __name__ == "__main__":
	common.check_python_version()
	options = common.check_and_parse_arguments(argument_parser())