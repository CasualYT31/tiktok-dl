"""Defines generic helper code useful for all tiktok-dl scripts.

Exports
-------
	* notice - Writes a message to the given text stream.
	* version_string - Returns the current version of the software.
	* check_python_version - Shuts down if the installed Python is old.
	* check_and_parse_arguments - Parses command-line arguments.
	* comfortable_terminal_height - The "effective" height of the
		terminal.
	* create_pages - Divides a chunk of text into pages.
	* print_pages - Prints strings to standard output as pages.
	* load_config - Loads a configuration file and returns it.
"""

import os
import sys
import io
from argparse import ArgumentParser
from argparse import Namespace

def write(msg: str, end: str = '\n', stream: io.TextIOBase = sys.stdout) \
	-> None:
	"""Outputs to the given text stream.
	
	Parameters
	----------
	msg : str
		The message to print.
	end : str
		The string to print at the end of `msg`. Defaults to '\n'.
	stream : io.TextIOBase
		The text stream to write the message to. Defaults to
		`sys.stdout`. If `None` is given, no message will be written.
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
		`sys.stdout`.
	"""
	
	write(f"[TIKTOK-DL] {msg}", stream=stream)

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
	
	if sys.version_info.major < 3 or sys.version_info.minor < 6:
		notice("Please use Python 3.6+!", stream)
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