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
	* clean_up_username - Cleans up a username, ready for processing.
	* clean_up_property_name - Cleans up a property name.
	* clean_up_link - Cleans up a link.
	* link_is_valid - Checks if a link is a valid TikTok video link.
	* date_is_valid - Checks if a date is in the right format.
	* comment_is_valid - Checks if a comment is valid for JSON storage.
	* extract_username_from_link - Get a TikTok user from a TikTok link.
	* UserConfig - Class representing a set of user configurations.
"""

import os
import sys
import io
import json
import re
import copy
from argparse import ArgumentParser
from argparse import Namespace
from xmlrpc.client import boolean

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

	if isinstance(username, str):
		return username.strip().lower()
	else:
		return username

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

	if isinstance(property, str):
		return property.strip().lower()
	else:
		return property

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

	if not isinstance(link, str):
		return link
	link = link.strip().lower()
	if link.find('?') >= 0:
		link = link[:link.find('?')]
	if link != "" and link[-1] == '/':
		link = link[:-1]
	return link

def clean_up_date(date: str) -> str:
	"""Cleans up a date, ready for processing.
	
	Parameters
	----------
	date : str
		The date to clean up.
	
	Returns
	-------
	str
		The cleaned up date string.
	"""

	if isinstance(date, str):
		return date.strip()
	else:
		return date

def link_is_valid(link: str) -> bool:
	"""Checks if the given link is valid.
	
	Parameters
	----------
	link : str
		The link to validate.
	
	Returns
	-------
	bool
		`True` if the link is a valid TikTok video link, `False`
		otherwise.
	"""

	if not isinstance(link, str):
		return False
	# This could be refined even further in the future.
	# E.g. I suspect that there can only be 19 numbers in a video ID,
	# and there are only some characters that are allowed in a username.
	if re.compile("https://www.tiktok.com/@.*/video/\\d*").fullmatch(link):
		return True
	else:
		return False

def date_is_valid(date: str) -> bool:
	"""Checks `date` to see if it is of the correct format.
	
	Parameters
	----------
	date : str
		The date to check.
	
	Returns
	-------
	bool
		`True` if the date is valid, `False` otherwise.
	"""
	
	if not isinstance(date, str):
		return False
	if re.compile("\\d{8}").fullmatch(date):
		return True
	else:
		return False

def comment_is_valid(comment: str) -> bool:
	"""Checks `comment` to see if it is of the correct format.
	
	Parameters
	----------
	comment : str
		The comment to check.
	
	Returns
	-------
	bool
		`True` if the comment is valid, `False` otherwise.
	"""
	
	return isinstance(comment, str)

def extract_username_from_link(link: str) -> str:
	"""Extracts the user from a TikTok video link.
	
	This function cleans up the username and link.

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

	link = clean_up_link(link)
	if (link_is_valid(link)):
		username = link[link.find('@') + 1:]
		return clean_up_username(username[:username.find('/')])
	else:
		raise ValueError()

class IgnoreError(Exception):
	"""Raised when "ignore" was used with `UserConfig.set()`."""
	pass

class UserConfig:
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
	
	# "Public" methods page 1.

	def user_is_configured(self, user: str) -> bool:
		"""Sees if a user has a configuration object.
		
		Parameters
		----------
		user : str
			The user to query.
		
		Returns
		-------
		bool
			`True` if the user exists in the configuration object,
			`False` if not.
		"""

		return clean_up_username(user) in self.config
	
	# Helper methods. Avoid calling these from outside of the class.

	def __create_new_user(self, config: dict, user: str) -> None:
		"""Creates a new user object for a given configuration.

		Parameters
		----------
		config : dict
			The configuration object to change.
		user : str
			The name of the user.
		"""

		user = clean_up_username(user)
		config[user] = {'notbefore': "20000101", 'ignore': [], 'comment': ""}
	
	def __set_property(self, user: str, property: str, value) -> None:
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
		"""

		user = clean_up_username(user)
		property = clean_up_property_name(property)
		if not self.user_is_configured(user):
			self.__create_new_user(self.config, user)
		self.config[user][property] = value
	
	def __get_property(self, user: str, property: str):
		"""Gets a property from a user's configuration object.

		Parameters
		----------
		user : str
			The name of the user.
		property : str
			The name of the property to get.

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

	# "Public" methods page 2.

	def load_config(self, filepath: os.path) -> None:
		"""Loads a UTF-8 configuration file into this object.

		This method only overwrites the currently stored configuration
		with the given script contents if it follows `tiktok-dl`'s
		format.

		All usernames, links, etc. will be cleaned up. In the case that
		two user objects exist, "AAA" and "aaa", "AAA" will be
		discarded. If there is just "AAA", then its object will be
		copied to "aaa" and the original "AAA" object will be deleted.
		If there are user objects "AAA" and "AaA", there will always be
		a user object "aaa" with either "AAA"'s values or "AaA"'s
		values. Whose values, though, is not guaranteed.
		
		Parameters
		----------
		filepath : os.path
			The path leading to the configuration file.
		
		Raises
		------
		Any exception that can be raised by `open()` or `json.load()`.
		TypeError, KeyError, ValueError
			When the given JSON script did not have the format that
			`tiktok-dl` expects.
		"""

		with open(filepath, encoding="UTF-8") as script:
			new_config = json.load(script)
		# Check new_config before setting it to self.config
		config = {}
		for key, value in new_config.items():
			new_key = clean_up_username(key)
			if new_key != key and new_key in new_config:
				# Skip "AAA" (see doc comment)
				continue
			self.__create_new_user(config, new_key)
			if date_is_valid(value["notbefore"]):
				config[new_key]["notbefore"] = value["notbefore"]
			else:
				raise ValueError()
			if comment_is_valid(value["comment"]):
				config[new_key]["comment"] = value["comment"]
			else:
				raise ValueError()
			if isinstance(value["ignore"], list) and \
				all([link_is_valid(link) for link in value["ignore"]]):
				config[new_key]["ignore"] = value["ignore"]
			else:
				raise ValueError()
		self.config = config
	
	def save_config(self, filepath: os.path) -> None:
		"""Saves this object to a UTF-8 configuration file.
		
		Parameters
		----------
		filepath : os.path
			The path leading to the file to create or overwrite.
	
		Raises
		------
		Any exception that can be raised by `open()` or `json.dump()`.
		"""

		with open(filepath, mode="w", encoding="UTF-8") as script:
			json.dump(self.config, script)

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
	
	def set_not_before(self, user: str, date: str) -> None:
		"""Set a user's "notbefore" property.

		If the given user doesn't currently exist in the configuration,
		a new user object will be created.
		
		Parameters
		----------
		user : str
			The user to set the "notbefore" property of.
		date : str
			The date in `YYYYMMDD` format.
		
		Raises
		------
		ValueError
			If the given date string was not in the correct format.
		"""
		
		date = clean_up_date(date)
		if not date_is_valid(date):
			raise ValueError()
		self.__set_property(user, "notbefore", date)

	def get_comment(self, user: str) -> str:
		"""Get a user's "comment" property.

		This property is ignored by `tiktok-dl` and is only seen by the
		user in `tiktok-config`.

		Parameters
		----------
		user : str
			The user to get the "comment" property of.
		
		Returns
		-------
		str
			The comment if the property is set, or a blank string if the
			property is not set.
		
		Raises
		------
		KeyError
			If the given user does not have a configuration object.
		"""
		
		return self.__get_property(user, "comment")
	
	def set_comment(self, user: str, comment: str) -> None:
		"""Set a user's "comment" property.

		If the given user doesn't currently exist in the configuration,
		a new user object will be created.
		
		Parameters
		----------
		user : str
			The user to set the "comment" property of.
		comment : str
			The comment.
		
		Raises
		------
		TypeError
			If the given comment was not a string.
		"""
		
		if not comment_is_valid(comment):
			raise ValueError()
		self.__set_property(user, "comment", comment)

	def set(self, property: str, user: str, value) -> str:
		"""Sets a property for a given user.
		
		Parameters
		----------
		property : str
			The string name for the property.
		user : str
			The name of the user to update.
		value
			The value to assign to the property.
		
		Returns
		-------
		str
			If a new user object was created, the name of the user is
			returned. A blank string otherwise.
		
		Raises
		------
		IgnoreError
			If the "ignore" property was given. This method does not
			support the "ignore" property.
		AttributeError
			If an invalid property was given.
		ValueError
			If the given value wasn't of the correct format for the
			property.
		"""

		ret = not self.user_is_configured(user)
		property = clean_up_property_name(property)
		if property == "notbefore":
			self.set_not_before(user, value)
		elif property == "comment":
			self.set_comment(user, value)
		elif property == "ignore":
			raise IgnoreError()
		else:
			raise AttributeError()
		if ret:
			return clean_up_username(user)
		else:
			return ""

	def get_ignore_links(self, user: str) -> list[str]:
		"""Copies a user's list of ignored links.
		
		Parameters
		----------
		user : str
			The user to get the "ignore" property of.
		
		Returns
		-------
		list[str]
			A deep copied list of ignored links.
		
		Raises
		------
		KeyError
			If the given user does not have a configuration object.
		"""

		user = clean_up_username(user)
		if self.user_is_configured(user):
			return copy.deepcopy(self.config[user]["ignore"])
		else:
			raise KeyError()

	def toggle_ignore_link(self, link: str) -> bool:
		"""Either adds or removes a link from the correct ignore list.
		
		Each user can have a list of links that are to be ignored when
		downloading. The user is extracted from the link, and that
		user's ignore list is changed.
		
		If the link is present within the user's ignore list, it is
		removed. If the link wasn't present, it is added.

		If the extracted user doesn't currently exist in the
		configuration, a new user object will be created.

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
		
		link = clean_up_link(link)
		user = extract_username_from_link(link)
		if user not in self.config:
			self.__create_new_user(self.config, user)
		if link in self.config[user]["ignore"]:
			self.config[user]["ignore"].remove(link)
			return False
		else:
			self.config[user]["ignore"].append(link)
			return True
	
	def delete_user(self, user: str) -> None:
		"""Deletes a user configuration object.
		
		Parameters
		----------
		user : str
			The name of the user to delete. Is cleaned up inside the
			method.
		
		Raises
		------
		KeyError
			If the given user did not exist.
		"""

		user = clean_up_username(user)
		if self.config.pop(user, None) == None:
			raise KeyError()
	
	def list_users(self, filter_re: str=".*") -> list[str]:
		"""Lists the users configured in this object.
		
		Parameters
		----------
		filter : str
			The regular expression which a username must fully match before
			before included in the returning list. Defaults to listing all
			users.
		
		Returns
		-------
		list[str]
			An ascending sorted list of usernames.
		
		Raises
		------
		re.error
			If the given regular expression was invalid.
		"""

		result = list(filter(re.compile(filter_re).fullmatch,
			list(self.config.keys())))
		result.sort()
		return result
	
	def user_to_string(self, user: str) -> str:
		"""Creates a readable string representation of a user's config.
		
		Parameters
		----------
		user : str
			The name of the user.
		
		Return
		------
		str
			The readable string.
		
		Raises
		------
		KeyError
			If the given user didn't exist at the time of calling.
		"""

		if self.user_is_configured(user):
			result = f"~~~{clean_up_username(user)}~~~\n"
			result += f"No videos from before: {self.get_not_before(user)}.\n"
			result += f"Comment: {self.get_comment(user)}\n"
			result += f"Ignoring {len(self.get_ignore_links(user))} links.\n"
			return result
		else:
			raise KeyError()