"""Defines generic helper code useful for all tiktok-dl scripts.

This script requires the following modules in order to run:
- `argparse`

Exports
-------
	* write - Writes a message to a stream, if a stream is given.
	* notice - Writes a `tiktok-dl` message to the given text stream.
	* version_string - Returns the current version of the software.
	* check_python_version - Shuts down if the installed Python is old.
	* check_and_parse_arguments - Parses command-line arguments.
	* comfortable_terminal_height - The "effective" height of the
		terminal.
	* create_pages - Divides a chunk of text into pages.
	* print_pages - Prints strings to standard output as pages.
	* load_config - Loads a configuration file and returns it.
	* clean_up_username - Cleans up a username, ready for processing.
	* clean_up_property_name - Cleans up a property name.
	* clean_up_link - Cleans up a link.
"""

import os
import sys
import io
import json
import re
from argparse import ArgumentParser
from argparse import Namespace

def write(msg: str, stream: io.TextIOBase = sys.stdout, end: str = '\n') \
	-> None:
	"""Outputs to the given text stream.
	
	Parameters
	----------
	msg : str
		The message to print.
	stream : io.TextIOBase
		The text stream to write the message to. Defaults to
		`sys.stdout`. If `None` is given, no message will be written.
	end : str
		The string to print at the end of `msg`. Defaults to '\n'.
	"""
	
	if stream is not None:
		stream.write(f"{msg}{end}")

def notice(msg: str, stream: io.TextIOBase = sys.stdout) -> None:
	"""Writes a tiktok-dl notice to the given text stream.
	
	The format of the message will always be: "[TIKTOK-DL] {msg}\n".
	
	Parameters
	----------
	msg : str
		The message to print.
	stream : io.TextIOBase
		The text stream to write the message to. Defaults to
		`sys.stdout`. Can be `None`, see `write()`.
	"""
	
	write(f"[TIKTOK-DL] {msg}", stream)

def version_string() -> str: # pragma: no cover
	"""Returns the current version of the software.
	
	Returns
	-------
	str
		Version string.
	"""
	
	return "tiktok-dl 1.0"

def check_python_version(stream: io.TextIOBase = sys.stderr) -> None:
	"""Checks the version of Python currently running.
	
	If the version of Python is below the minimum supported version, a
	message will be printed if a stream is given, and the program will
	exit. Otherwise, nothing happens.
	
	Parameters
	----------
	stream : io.TextIOBase
		The stream to write the message to. If `None` is given, no
		message will be written. Defaults to `sys.stderr`.
	"""
	
	if sys.version_info.major < 3 or sys.version_info.minor < 10:
		notice("Please use Python 3.10+!", stream)
		sys.exit(1)

def check_and_parse_arguments(parser: ArgumentParser, \
	stream: io.TextIOBase = sys.stderr) -> Namespace:
	"""Checks to see if any command-line arguments were given.
	
	If no command-line arguments were given, the `ArgumentParser` help
	string will be printed to the given stream and the program will
	exit.
	
	Parameters
	----------
	argparse.ArgumentParser
		The argument parser to use with this function call.
	stream : io.TextIOBase
		The stream to write the help to. If `None` is given, no message
		will be written. Defaults to `sys.stderr`.
	
	Returns
	-------
	argparse.Namespace
		In the case that command-line arguments were provided, they will
		be parsed and the resulting `Namespace` object will be returned.
	"""
	
	if len(sys.argv) < 2:
		parser.print_help(stream)
		sys.exit(1)
	else:
		return parser.parse_args()

def comfortable_terminal_height() -> int:
	"""Calculates the optimal size of a page for the current terminal.
	
	Returns
	-------
	int
		`os.get_terminal_size().lines - 3`. If the value returned is <=
		0, then it can be deduced that the height of the terminal is
		"not comfortable enough."
	"""
	
	return os.get_terminal_size().lines - 3

def create_pages(lines: str, lines_per_page: int = 0) -> list[str]:
	"""Divides a large string spanning multiple lines into pages.
	
	Parameters
	----------
	lines : str
		The large string to divide up.
	lines_per_page : int, optional
		The maximum number of lines a page can have. Defaults to 0. If
		<= 0 is given, the current terminal height in lines is queried.
		If the height is at least four lines, then `lines_per_page` will
		be set to the height of the terminal minus 3. If the height is
		less than four lines, one page will be created containing the
		entire string.
	
	Returns
	-------
	list of str
		A list of pages.
	"""
	
	line_list = lines.split("\n")
	if lines_per_page <= 0:
		height = comfortable_terminal_height()
		if height >= 1:
			lines_per_page = height
		else:
			lines_per_page = len(line_list)
	pages = [""]
	for i in range(len(line_list)):
		if i != 0 and i % lines_per_page == 0:
			pages.append("")
		pages[-1] += line_list[i]
		if i < len(line_list) - 1:
			pages[-1] += "\n"
	return pages

def print_pages(pages: list[str]):
	"""Prints a list of strings to the console as a set of pages.
	
	I figured this kind of function was only really useful for the
	terminal, so I didn't add support for other streams here.
	
	Parameters
	----------
	pages : list of str
		The pages to print. If the list is empty, the function will
		return without printing anything.
	"""
	
	for i, page in enumerate(pages):
		print(page)
		print(f"Page {i + 1} out of {len(pages)}", end='')
		if i == 0:
			print(" (press enter to continue)", end='')
		print("...", end='')
		input()
		if i < len(pages) - 1:
			print()

def load_config(filepath: os.path) -> dict:
	"""Loads a given UTF-8 configuration file and returns it.
	
	Parameters
	----------
	filepath : os.path
		The path leading to the configuration file.
	
	Returns
	-------
	dict
		The root JSON object containing all of the user objects.
	
	Raises
	------
	Any exception that can be raised by `open()` or `json.load()`.
	"""
	
	with open(filepath, encoding="UTF-8") as script:
		return json.load(script)

def save_config(filepath: os.path, config: dict) -> None:
	"""Saves a given UTF-8 configuration file.
	
	Parameters
	----------
	filepath : os.path
		The path leading to the file to overwrite with the configuration
		object. Will create the file if it doesn't exist already.
	config : dict
		The configuration object to save.
	
	Raises
	------
	Any exception that can be raised by `open()` or `json.dump()`.
	"""
	
	with open(filepath, mode="w", encoding="UTF-8") as script:
		json.dump(config, script)

def clean_up_username(username: str) -> str:
	"""Cleans up a username, ready for processing.
	
	Parameters
	----------
	username : str
		The username to clean up.
	
	Returns
	-------
	str
		The cleaned up username.
	"""

	return username.strip().lower()

def clean_up_property_name(property: str) -> str:
	"""Cleans up a property name, ready for processing.
	
	Parameters
	----------
	property : str
		The property name to clean up.
	
	Returns
	-------
	str
		The cleaned up property name.
	"""

	return property.strip().lower()

def clean_up_link(link: str) -> str:
	"""Cleans up a link, ready for processing.
	
	Parameters
	----------
	link : str
		The link to clean up.
	
	Returns
	-------
	str
		The cleaned up link.
	"""

	link = link.strip().lower()
	if link.find('?') >= 0:
		link = link[:link.find('?')]
	if link != "" and link[-1] == '/':
		link = link[:-1]
	return link

def link_is_valid(link: str) -> bool:
	"""Checks if the given link is valid.
	
	Parameters
	----------
	link : str
		The link to validate.
	
	Returns
	-------
	bool
		`True` if the link is a valid TikTok video link, `False` otherwise.
	"""

	# This could be refined even further in the future.
	# E.g. I suspect that there can only be 19 numbers in a video ID,
	# and there are only some characters that are allowed in a username.
	return re.compile("https://www.tiktok.com/@.*/video/\\d*").fullmatch(link)

def extract_username_from_link(link: str) -> str:
	"""Extracts the user from a TikTok video link.
	
	This function does not clean up the username or link.

	Parameters
	----------
	link : str
		The TikTok video link to extract from.
	
	Returns
	-------
	The username.

	Raises
	------
	ValueError
		When the given link wasn't a valid TikTok video link.
	"""

	if (link_is_valid(link)):
		username = link[link.find('@') + 1:]
		return username[:username.find('/')]
	else:
		raise ValueError()

class user_config:
	"""Holds the tiktok-dl configurations for a collection of TikTok
	users.
	
	The benefit of using this class is that it will always clean up all
	of the inputs (usernames, links, etc.), and will allow you to
	interact with tiktok-dl configurations via a single interface,
	without relying directly on the way the configurations are
	formatted or stored. It will also perform all error handling for
	you (though you should still catch any exceptions that are raised).
	"""

	def __init__(self):
		"""Initialises the configuration with an empty root object."""

		self.config = {}
	
	# Helper methods. Avoid calling these from outside of the class.

	def __create_new_user(self, user: str) -> None:
		"""Creates a new user object for this configuration.

		Parameters
		----------
		user : str
			The name of the user.
		"""

		user = clean_up_username(user)
		self.config[user]["notbefore"] = ""
		self.config[user]["ignore"] = []
		self.config[user]["comment"] = ""
	
	def __set_property(self, user: str, property: str, value) -> bool:
		"""Sets a property in a user's configuration object.
		
		Creates the user's configuration object if it didn't already
		exist.

		Parameters
		----------
		user : str
			The name of the user.
		property : str
			The name of the property to update.
		value
			The value to set to the property.

		Returns
		-------
		bool
			`True` if the user object had to be created, `False` if the
			user already existed.
		"""

		user = clean_up_username(user)
		property = clean_up_property_name(property)
		ret = user not in self.config
		if ret:
			self.__create_new_user(user)
		self.config[user][property] = value
		return ret
	
	def __get_property(self, user: str, property: str):
		"""Gets a property from a user's configuration object.

		Parameters
		----------
		user : str
			The name of the user.
		property : str
			The name of the property to get.
		value
			The value to set to the property.

		Returns
		-------
		The value stored in the property.

		Raises
		------
		KeyError
			If the given user did not have a configuration object.
		ValueError
			If the given property is not recognised by tiktok-dl.
		"""

		user = clean_up_username(user)
		property = clean_up_property_name(property)
		if user in self.config:
			if property in self.config[user]:
				return self.config[user][property]
			else:
				raise ValueError()
		else:
			raise KeyError()

	# "Public" methods.

	def get_not_before(self, user: str) -> str:
		"""Get a user's "notbefore" property.

		This property tells tiktok-dl not to download videos uploaded by
		the given user and before the given date. By default, this
		property is not present.

		Parameters
		----------
		user : str
			The user to get the "notbefore" property of.
		
		Returns
		-------
		str
			The date in `YYYYMMDD` format if the property is set, or a
			blank string if the property is not set.
		
		Raises
		------
		KeyError
			If the given user does not have a configuration object.
		"""
		
		return self.__get_property(user, "notbefore")
	
	def set_not_before(self, user: str, date: str) -> bool:
		"""Set a user's "notbefore" property.

		If the given user doesn't currently exist in the configuration,
		a new user object will be created.
		
		Parameters
		----------
		user : str
			The user to set the "notbefore" property of.
		date : str
			The date in `YYYYMMDD` format.
		
		Returns
		-------
		bool
			`True` if a new user object was created, `False` if the user
			already had a configuration object.
		
		Raises
		------
		ValueError
			If the given date string was not in the correct format.
		"""
		
		if not re.compile("\\d{7}").fullmatch(date):
			raise ValueError()
		return self.__set_property(user, "notbefore", date)

	def toggle_ignore(link: str) -> bool:
		"""Either adds or removes a link from the correct ignore list.
		
		Each user can have a list of links that are to be ignored when
		downloading. The user is extracted from the link, and that
		user's ignore list is changed.
		
		If the link is present within the user's ignore list, it is
		removed. If the link wasn't present, it is added.

		Parameters
		----------
		link : str
			The link to add/delete.
		
		Returns
		-------
		bool
			`True` if the link was added, `False` if the link was
			removed.
		
		Raises
		------
		ValueError
			If the given link was invalid.
		"""
		
		pass