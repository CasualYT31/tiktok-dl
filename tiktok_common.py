"""Defines generic helper code useful for all tiktok-dl scripts.

This script requires the following modules in order to run:
- `argparse`

Exports
-------
	* the_same_filepath - Finds out if two paths point to the same file.
	* write - Writes a message to a stream, if a stream is given.
	* notice - Writes a `tiktok-dl` message to the given text stream.
	* version_string - Returns the current version of the software.
	* check_python_version - Shuts down if the installed Python is old.
	* check_and_parse_arguments - Parses command-line arguments.
	* comfortable_terminal_height - "Effective" height of the console.
	* create_pages - Divides a chunk of text into pages.
	* print_pages - Prints strings to standard output as pages.
	* clean_up_username - Cleans up a username, ready for processing.
	* clean_up_property_name - Cleans up a property name.
	* clean_up_link - Cleans up a link.
	* clean_up_date - Cleans up a date string.
	* username_is_valid - Checks if a string is a valid TikTok username.
	* link_is_valid - Checks if a link is a valid TikTok video link.
	* date_is_valid - Checks if a date is in the right format.
	* comment_is_valid - Checks if a comment is valid for JSON storage.
	* extract_username_from_link - Get a TikTok user from a TikTok link.
	* IgnoreError - Raised when "ignore" is given to `UserConfig.set()`.
	* UserConfig - Class representing a set of user configurations.
"""

from dataclasses import dataclass
import os
import sys
import io
import json
import re
import copy
from enum import Enum, unique
from argparse import ArgumentParser
from argparse import Namespace

def the_same_filepath(path1: str, path2: str) -> bool:
	"""Finds out if two paths point to the same file.

	Parameters
	----------
	path1 : str
		The first path.
	path2 : str
		The second path.
	
	Returns
	-------
	bool
		`True` if both paths point to the same file, `False` if not, or
		if an exception was thrown.
	"""

	try:
		return os.path.samefile(path1, path2)
	except:
		return False

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

@dataclass(frozen=True)
class Username:
	"""Represents a TikTok username."""

	def __init__(self, user: str):
		"""Assigns the username to store in this instance.
		
		Automatically cleans up the input and stores it within the
		`name` property.
		
		Parameters
		----------
		user : str
			The username to store.
		"""
		
		object.__setattr__(self, "name", user.strip().lower())
	
	def __str__(self) -> str:
		"""Returns the username."""

		return self.name
	
	def __repr__(self) -> str:
		return self.__str__()

	def __eq__(self, other) -> bool:
		if isinstance(other, Username):
			return self.name == other.name
		elif isinstance(other, str):
			return self.name == other

	def is_valid(self) -> bool:
		"""Determines if a valid username is stored.
		
		Returns
		-------
		bool
			`True` if there is at least one lower-case letter, number,
			_ or . in the username, `False` otherwise.
		"""
		
		if re.compile("[a-z\\d_.]+").fullmatch(self.name):
			return True
		else:
			return False

@dataclass(frozen=True)
class Link:
	"""Represents a TikTok video link."""

	def __init__(self, link: str):
		"""Assigns the link to store in this instance.
		
		Automatically cleans up the input and stores it within the
		`link` property. If the link is valid, the username will also be
		extracted and stored in the `user` property.
		
		Parameters
		----------
		link : str
			The link to store. If a non-string, a blank link is stored.
		"""
		
		link = link.strip().lower()
		if link.find('?') >= 0:
			link = link[:link.find('?')]
		if link != "" and link[-1] == '/':
			link = link[:-1]
		object.__setattr__(self, "link", link)
		if self.is_valid():
			user = link[link.find('@') + 1:]
			object.__setattr__(self, "user", Username(user[:user.find('/')]))
		else:
			object.__setattr__(self, "user", Username(""))
	
	def __str__(self) -> str:
		"""Returns the link."""
		
		return self.link
	
	def __repr__(self) -> str:
		return self.user + " in " + self.link

	def __eq__(self, other) -> bool:
		if isinstance(other, Link):
			return self.link == other.link
		elif isinstance(other, str):
			return self.link == other

	def is_valid(self) -> bool:
		"""Determines if a valid link is stored.
		
		Returns
		-------
		bool
			`True` if a plain TikTok video link is stored, `False`
			otherwise.
		"""
		
		expression = "https://www.tiktok.com/@[a-z\\d_.]+/video/\\d{19}"
		if re.compile(expression).fullmatch(self.link):
			return True
		else:
			return False

@dataclass(frozen=True)
class Date:
	"""Represents a `yt-dlp` date string."""

	def __init__(self, date: str):
		"""Assigns the date to store in this instance.
		
		Automatically cleans up the input and stores it within the
		`date` property.
		
		Parameters
		----------
		date : str
			The date to store.
		"""

		object.__setattr__(self, "date", date.strip())
	
	def __str__(self) -> str:
		"""Returns the date."""
		
		return self.date
	
	def __repr__(self) -> str:
		return self.__str__()

	def __eq__(self, other) -> bool:
		if isinstance(other, Date):
			return self.date == other.date
		elif isinstance(other, str):
			return self.date == other
	
	def is_valid(self) -> bool:
		"""Determines if a valid date is stored.
		
		Returns
		-------
		bool
			`True` if a YYYYMMDD date is stored, `False` otherwise.
		"""

		if re.compile("\\d{8}").fullmatch(self.date):
			return True
		else:
			return False

@unique
class Property(Enum):
	"""Represents a `tiktok-config` property."""
	
	NOT_BEFORE = "notbefore"
	COMMENT = "comment"
	IGNORE = "ignore"

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

	Note that if a string is given for a username, link, or date, it
	will be automatically converted into the proper type automatically.
	"""

	def __init__(self):
		"""Initialises the configuration with an empty root object."""

		self.config = {}
	
	# "Public" methods page 1.

	def user_is_configured(self, user: Username) -> bool:
		"""Sees if a user has a configuration object.
		
		Parameters
		----------
		user : Username
			The user to query.
		
		Returns
		-------
		bool
			`True` if the user exists in the configuration object,
			`False` if not.
		"""

		if isinstance(user, str):
			user = Username(user)
		return user in self.config
	
	# Helper methods. Avoid calling these from outside of the class.

	def __create_new_user(self, config: dict, user: Username) -> None:
		"""Creates a new user object for a given configuration.

		Parameters
		----------
		config : dict
			The configuration object to change.
		user : Username
			The name of the user.
		
		Raises
		------
		KeyError
			If the given username was invalid.
		"""

		if not user.is_valid():
			raise KeyError()
		config[user] = {'notbefore': "20000101", 'ignore': [], 'comment': ""}
	
	def __set_property(self, user: Username, property: Property, value) -> None:
		"""Sets a property in a user's configuration object.
		
		Creates the user's configuration object if it didn't already
		exist.

		Parameters
		----------
		user : Username
			The name of the user.
		property : Property
			The name of the property to update.
		value
			The value to set to the property.
		"""

		if not self.user_is_configured(user):
			self.__create_new_user(self.config, user)
		self.config[user][property] = value
	
	def __get_property(self, user: Username, property: Property):
		"""Gets a property from a user's configuration object.

		Parameters
		----------
		user : Username
			The name of the user.
		property : Property
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
			new_key = Username(key)
			if new_key != key and new_key in new_config:
				# Skip "AAA" (see doc comment)
				continue
			self.__create_new_user(config, new_key)
			date = Date(value[Property.NOT_BEFORE.value])
			if date.is_valid():
				config[new_key][Property.NOT_BEFORE.value] = date
			else:
				raise ValueError()
			config[new_key][Property.COMMENT.value] = \
				value[Property.COMMENT.value]
			for link in value[Property.IGNORE.value]:
				new_link = Link(link)
				if new_link.is_valid():
					config[new_key][Property.IGNORE.value].append(new_link)
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

	def get_not_before(self, user: Username) -> Date:
		"""Get a user's "notbefore" property.

		This property tells tiktok-dl not to download videos uploaded by
		the given user and before the given date. By default, this
		property is not present.

		Parameters
		----------
		user : Username
			The user to get the "notbefore" property of.
		
		Returns
		-------
		Date
			The date in `YYYYMMDD` format if the property is set, or a
			blank string if the property is not set.
		
		Raises
		------
		KeyError
			If the given user does not have a configuration object.
		"""
		
		if isinstance(user, str):
			user = Username(user)
		return self.__get_property(user, Property.NOT_BEFORE.value)
	
	def set_not_before(self, user: Username, date: Date) -> None:
		"""Set a user's "notbefore" property.

		If the given user doesn't currently exist in the configuration,
		a new user object will be created.
		
		Parameters
		----------
		user : Username
			The user to set the "notbefore" property of.
		date : Date
			The date in `YYYYMMDD` format.
		
		Raises
		------
		ValueError
			If the given date string was not in the correct format.
		"""
		
		if isinstance(user, str):
			user = Username(user)
		if isinstance(date, str):
			date = Date(date)
		if not date.is_valid():
			raise ValueError()
		self.__set_property(user, Property.NOT_BEFORE.value, date)

	def get_comment(self, user: Username) -> str:
		"""Get a user's "comment" property.

		This property is ignored by `tiktok-dl` and is only seen by the
		user in `tiktok-config`.

		Parameters
		----------
		user : Username
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
		
		if isinstance(user, str):
			user = Username(user)
		return self.__get_property(user, Property.COMMENT.value)
	
	def set_comment(self, user: Username, comment: str) -> None:
		"""Set a user's "comment" property.

		If the given user doesn't currently exist in the configuration,
		a new user object will be created.
		
		Parameters
		----------
		user : Username
			The user to set the "comment" property of.
		comment : str
			The comment.
		
		Raises
		------
		TypeError
			If the given comment was not a string.
		"""
		
		if isinstance(user, str):
			user = Username(user)
		self.__set_property(user, Property.COMMENT.value, comment)

	def set(self, property: Property, user: Username, value) -> Username:
		"""Sets a property for a given user.
		
		Parameters
		----------
		property : Property
			The string name for the property.
		user : Username
			The name of the user to update.
		value
			The value to assign to the property.
		
		Returns
		-------
		Username
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
		KeyError
			If the given username was invalid.
		"""

		if isinstance(user, str):
			user = Username(user)
		ret = not self.user_is_configured(user)
		if property == Property.NOT_BEFORE.value:
			self.set_not_before(user, value)
		elif property == Property.COMMENT.value:
			self.set_comment(user, value)
		elif property == Property.IGNORE.value:
			raise IgnoreError()
		else:
			raise AttributeError()
		if ret:
			return user
		else:
			return Username("")

	def get_ignore_links(self, user: Username) -> list[Link]:
		"""Copies a user's list of ignored links.
		
		Parameters
		----------
		user : Username
			The user to get the "ignore" property of.
		
		Returns
		-------
		list[Link]
			A deep copied list of ignored links.
		
		Raises
		------
		KeyError
			If the given user does not have a configuration object.
		"""

		if isinstance(user, str):
			user = Username(user)
		if self.user_is_configured(user):
			return [Link(link) for link in self.config[user][Property.IGNORE.value]]
		else:
			raise KeyError()

	def toggle_ignore_link(self, link: Link) -> bool:
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
		link : Link
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
		
		if isinstance(link, str):
			link = Link(link)
		if link.user not in self.config:
			self.__create_new_user(self.config, link.user)
		if link in self.config[link.user][Property.IGNORE.value]:
			self.config[link.user][Property.IGNORE.value].remove(link)
			return False
		else:
			self.config[link.user][Property.IGNORE.value].append(link)
			return True
	
	def delete_user(self, user: Username) -> None:
		"""Deletes a user configuration object.
		
		Parameters
		----------
		user : Username
			The name of the user to delete. Is cleaned up inside the
			method.
		
		Raises
		------
		KeyError
			If the given user did not exist.
		"""

		if isinstance(user, str):
			user = Username(user)
		if self.config.pop(user, None) == None:
			raise KeyError()
	
	def list_users(self, filter_re: str=".*") -> list[Username]:
		"""Lists the users configured in this object.
		
		Parameters
		----------
		filter : str
			The regular expression which a username must fully match before
			before included in the returning list. Defaults to listing all
			users.
		
		Returns
		-------
		list[Username]
			An ascending sorted list of usernames.
		
		Raises
		------
		re.error
			If the given regular expression was invalid.
		"""

		result = list(filter(re.compile(filter_re).fullmatch,
			[key.name for key in self.config.keys()]))
		result.sort()
		return result
	
	def user_to_string(self, user: Username) -> str:
		"""Creates a readable string representation of a user's config.
		
		Parameters
		----------
		user : Username
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

		if isinstance(user, str):
			user = Username(user)
		if self.user_is_configured(user):
			result = f"~~~{user}~~~\n"
			result += f"No videos from before: {self.get_not_before(user)}.\n"
			result += f"Comment: {self.get_comment(user)}\n"
			result += f"Ignoring {len(self.get_ignore_links(user))} links.\n"
			return result
		else:
			raise KeyError()