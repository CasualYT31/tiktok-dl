"""TikTok Video Downloader Utility

As a command-line program, this script can be used to download TikTok
videos and store them in separate folders by user.

As a module, this script offers the functionality of the above whilst
allowing you to write your own scripts that work with tiktok-dl.

This script requires the following modules in order to run:
- `argparse`
- `yt-dlp`
- `requests_html`
- `numpy`
It also requires at least Python 3.10.

Terminology
-----------
It is important to define what we mean by "user", "username", "link",
etc.
Date
	Dates for yt-dlp take the format YYYYMMDD, so tiktok-dl uses this
	format, too.
Link
	Will always refer to a link to a single video when this term is used
	within `tiktok_` scripts. Links can have the form
	`https://www.tiktok.com/@gordonramsayofficial/video/7127714692314729733`
	or the form
	`https://www.tiktok.com/@gordonramsayofficial/video/7127714692314729733?is_copy_url=1&is_from_webapp=v1`
	i.e. they must always have the correct username and a video ID. It
	should be noted that all `?` options are removed from links before
	they get processed in this script as well as other scripts like
	`tiktok_config.py`.
User [Page]
	A TikTok user. Can often refer to a TikTok user's page, i.e.
	`https://www.tiktok.com/@gordonramsayofficial`.
Username
	Will refer to the @ of a given user. Note, however, that the @
	character is never included when the term "username" is used. For
	example, `gordonramsayofficial` is a username.

Accepted Input
--------------
`tiktok-dl` accepts several different types of input. There is an order
of precedence when it comes to determining the type of input, i.e. it
will see if it is 1 first, and if not, 2, etc.
1. Links.
	If a link is recognised as a valid TikTok video link, it will be
	accepted as a single link to download.
2. Filenames.
	If the given input is the name of a file that exists, it will
	attempt to open it and read from it. This program accepts two file
	formats:
	- HTML
		If the file begins with `<!DOCTYPE html>`, it will be treated as
		a HTML download of a TikTok page. See the `HTML Input` section
		for more information.
	- TXT
		Otherwise, the file will be treated as a plain text file, where
		one input should be on one line. "Input" can include a link, a
		username, or even another filename.
3. Usernames.
	If the input is a valid TikTok username, it will use either `yt-dlp`
	or `requests_html` to scrape from that user's page the links to all
	of their videos, and feed them in as input. The list of input
	usernames will be written to a file if `tiktok-dl` is configured to
	do so; please see the `--history` and `--no-history` options.
	**IMPORTANT: see User Page Scraping section for more information.**
4. Any other input is considered invalid. It will be reported to the
	console, and it will be ignored.

Command-Line Options
--------------------
--help
	Prints the module's docstring then exits.
--version
	Prints the version number for this program, then exits.
--config filename
	Points to where the configuration script resides. By default, it
	will look for it in `./config.json`, i.e. in the current working
	directory. Please read the documentation in `tiktok_config.py` for
	more information.
--ignore link
	Will ensure that the given link is ignored, i.e. is removed from the
	list of links to download. This will NOT add the link to the
	configuration file.
--list filename
	Instead of downloading any videos, `tiktok-dl` will simply write all
	of the input links into the specified text file. The file will be
	overwritten. The number of links will be printed after writing.
--user-method ytdlp | html
	Specifies the method via which user pages will be downloaded. By
	default, `ytdlp` is used. However, the `html` method can be used to
	scrape the newest ~30 links from the given user directly from
	TikTok using `requests_html`. When using the `html` method for the
	first time, `requests_html` will download Chromium (~137MB).
	**IMPORTANT: see User Page Scraping section for more information.**
--delete-after input
	Accepts the given parameter as input like normal. However, if the
	input is a filename, the file will be deleted after all of the
	inputted links have been processed.
--history filename
	A list of usernames that were input will be generated and will be
	written to `./usernames.txt` by default. Use this option to
	overwrite a different file.
--no-history
	If this option is given, no username history will be recorded to any
	file.
--split n
	This option will split all the input links up as evenly as possible
	into n groups, and then run n threads, one thread per group of input
	links, and `tiktok-dl` will then download all of the links in
	parallel. Unlike usual, no live updates will be printed to the
	console, and instead a summary of the downloading process will be
	printed at the end.

User Page Scraping
------------------
Unfortunately, `yt-dlp`'s TikTok user page scraping feature has stopped
working as of July 2022. This is probably due to a change in the way
TikTok handles requests that `yt-dlp` hasn't been programmed to handle
yet. I am monitoring the situation over at
https://github.com/yt-dlp/yt-dlp/issues/3776 and will update this
project once it starts working again. In the mean time, use other
methods to scrape from user pages, such as `html`—WHICH WILL BE THE
DEFAULT WHILST YT-DLP DOESN'T WORK—and by providing complete HTML
pages as described below.

HTML Input
----------
One method of downloading a user's videos using `tiktok-dl` is to
download the *complete* HTML of the user page, and then feed in just the
HTML file as input. This will include all of the video links that you've
loaded on the page, which could be all of them if you scroll all the way
down to a user's first video.

All you have to do is open the user page in a browser (it works on both
Firefox and Chrome, other browsers should work too), scroll to reveal as
many videos as you want, and then hit Ctrl+S. Make sure to download the
complete HTML page, which will download name.html and a `name_files`
folder. I have noted that Firefox tends to download pages a lot quicker
than Chrome.

One upside of this method is that you can also include links of the
original videos that the user has duetted and stitched with. The major
downside is that, with user pages containing thousands of videos, it
takes time, and after so many videos, the page lags like crazy and it
becomes increasingly difficult to keep on scrolling.

I added this method to download videos because I wasn't aware at the
time that `yt-dlp` could download whole user pages. Whenever possible,
prefer supplying the username as input rather than a HTML file. It is
still an invaluable backup option, though, in cases where you want to
include original videos of duets, or when `yt-dlp` user page scraping
[temporarily] stops working.

Exports
-------
	* YtDlpLogger - Logger class to redirect `yt-dlp` output.
	* thread_count - The type of argument that --split is.
	* argument_parser - Constructs the tiktok-dl argument parser.
	* scrape_from_user - Scrape links from a TikTok user's page.
	* scrape_from_file - Processes inputs from files.
	* process_inputs - Finds all the links in the given list of inputs.
	* update_history - Updates a username history file with more users.
"""

import os
import re
import shutil
from threading import Thread
from copy import deepcopy
from sys import stdout
from io import TextIOBase
from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError
from requests_html import HTMLSession
from pyppeteer.errors import TimeoutError
from numpy import array_split
import tiktok_common as common
from tiktok_common import UserConfig, clean_up_link
import tiktok_config as t

DEFAULT_USER_METHOD = "html"

class YtDlpLogger:
	"""Logger used to divert `yt-dlp` output to a given stream."""

	def __init__(self, stream: TextIOBase=stdout):
		"""Initialises this logger with a stream.
		
		Parameters
		----------
		stream : io.TextIOBase
			The stream to print messages to. Defaults to `sys.stdout`.
			Can be `None`.
		"""

		self.stream = stream

	def debug(self, msg):
		if msg.startswith('[debug] '):
			pass
		else:
			self.info(msg)

	def info(self, msg):
		common.notice(msg, self.stream)

	def warning(self, msg):
		common.notice(msg, self.stream)

	def error(self, msg):
		common.notice(msg, self.stream)

def TiktokDL(stream: TextIOBase=stdout, extra_opts: dict={}) -> YoutubeDL:
	"""Constructs a `YoutubeDL` object with a set of tiktok-dl options.

	Parameters
	----------
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	extra_opts : dict
		More YoutubeDL options to add to the YoutubeDL object. Any
		values given in this parameter will overwrite the value in this
		function's options if there are any matching keys. Defaults to
		no extra options.
	
	Returns
	-------
	YoutubeDL
		A `yt-dlp` object.
	"""

	ydl_opts = {
		"logger": YtDlpLogger(stream)
	}
	ydl_opts.update(extra_opts)
	return YoutubeDL(ydl_opts)

def thread_count(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise ArgumentTypeError(f"{value} is an invalid thread number, must "
			"be > 0")
    return ivalue

def argument_parser() -> ArgumentParser:
	"""Generates an argument parser for tiktok-dl.
	
	Returns
	-------
	argparse.ArgumentParser
		The argument parser that is compatible with tiktok-dl.
	"""

	parser = ArgumentParser( add_help=False,
		description="Downloads and sorts TikTok videos.")
	parser.add_argument('-h', '--help', action='store_true')
	parser.add_argument('-v', '--version', action='version', \
		version=common.version_string())
	parser.add_argument('-c', '--config', default='./config.json', \
		metavar='CONFIGPATH')
	parser.add_argument('-i', '--ignore', action='append', \
		metavar='LINK')
	parser.add_argument('-l', '--list', metavar='FILEPATH')
	parser.add_argument('-u', '--user-method', choices=['ytdlp', 'html'], \
		default=DEFAULT_USER_METHOD, metavar='METHOD')
	parser.add_argument('-d', '--delete-after', action='append', \
		metavar='FILE')
	parser.add_argument('--history', default='./usernames.txt', \
		metavar='FILEPATH')
	parser.add_argument('-n', '--no-history', action='store_true')
	parser.add_argument('-s', '--split', type=thread_count, default=1,
		metavar='THREADS')
	parser.add_argument('input', nargs='*', metavar='INPUT')
	return parser

def scrape_from_user(user: str, session: YoutubeDL=None,
	stream: TextIOBase=stdout) -> set[str]:
	"""Scrapes links from a user's page.

	Parameters
	----------
	user : str
		The user to scrape from.
	session : YoutubeDL
		The `yt-dlp` session to use if the 'ytdlp' method is required.
		If `None`, the `html` method is used. Defaults to `None`.
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	
	Returns
	-------
	set of str
		A set of extracted links.
	"""

	common.notice(f"Scraping from user \"{user}\".")
	if session is None:
		# html method
		html_session = HTMLSession()
		page = html_session.get(f"https://www.tiktok.com/@{user}")
		for i in range(1,2):
			try:
				page.html.render(wait=1.0, scrolldown=10, sleep=1.0)
				break
			except TimeoutError:
				if i == 1:
					common.notice(f"Scraping from user \"{user}\" timed out, "
						"will retry once.", stream)
				elif i == 2:
					common.notice(f"Failed to scrape for user \"{user}\".")
		return set(filter(
			lambda link : True if link.find("/video/") != -1 else False,
			page.html.absolute_links))
	else:
		# ytdlp method
		links = set()
		try:
			info = session.extract_info(f"https://www.tiktok.com/@{user}",
				download=False)
			for entry in info['entries']:
				links.add("https://www.tiktok.com/"
					f"{entry['webpage_url_basename']}/video/{entry['id']}")
		except (DownloadError, ExtractorError):
			common.notice(f"Failed to scrape for user \"{user}\".")
		return links

def __process_inputs__(inputs, user_method, stream):
	"""Internal function: use process_inputs instead!

	Used to forward declare the process_input function so that scrape_from_file
	can call it.
	"""

	pass
__process_inputs = __process_inputs__

def scrape_from_file(path: str, session: YoutubeDL=None,
	stream: TextIOBase = stdout) -> tuple[set[str],set[str],set[str]]:
	"""Scrapes inputs from a given file.

	If the given file is determined to be an HTML script, the links will
	be scraped and returned. Otherwise, the file is treated as a text
	file, where each line represents one input that is passed to
	`process_inputs`.
	
	Parameters
	----------
	path : str
		Path to the file to read from.
	session : YoutubeDL
		The `yt-dlp` session to use if the 'ytdlp' method is required
		for scraping from user pages. If `None`, the `html` method is
		used. Defaults to `None`.
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	
	Returns
	-------
	Same as `process_inputs`.
	"""

	with open(path, encoding="UTF-8") as file:
		contents = [line.strip() for line in file.readlines()]
	if len(contents) == 0:
		return set(), set(), set()
	elif contents[0] == "<!DOCTYPE html>":
		links = set()
		for line in contents:
			# Most likely a cleaner way of implementing this, e.g. match
			# against valid links, not just ones with /video/ in them.
			links_are_at = [m.start() for m in re.finditer("/video/", line)]
			for i in links_are_at:
				before = line[:i]
				after = line[i:]
				first_half = before[before.rfind("https://"):]
				second_half = after[:after.find("\"")]
				link = first_half + second_half
				if common.link_is_valid(link):
					links.add(link)
		return links, set(), set([path])
	else:
		# Before passing it to process_inputs, remove any instances of "path"
		# in the file to prevent RecursionErrors. Also remove blank lines.
		contents = [line for line in contents \
			if line != "" and not common.the_same_filepath(path, line)]
		return __process_inputs(contents, session, stream)

def __process_inputs_internal(inputs, session, stream):
	links = set()
	users = set()
	htmls = set()
	for input in inputs:
		if common.link_is_valid(common.clean_up_link(input)):
			links.add(common.clean_up_link(input))
		elif Path(input).is_file():
			(new_links, new_users, new_htmls) = \
				scrape_from_file(input, session, stream)
			links = links.union(new_links)
			users = users.union(new_users)
			htmls = htmls.union(new_htmls)
		elif common.username_is_valid(common.clean_up_username(input)):
			links = links.union(scrape_from_user(input, session, stream))
			users.add(common.clean_up_username(input))
		else:
			common.notice(f"Invalid input: {input}", stream)
	return (links, users, htmls)

def process_inputs(inputs: list[str], method: str=DEFAULT_USER_METHOD,
	stream: TextIOBase = stdout) -> tuple[set[str],set[str],set[str]]:
	"""Scrapes all of the links from a given list of inputs.
	
	Parameters
	----------
	inputs : list of str
		List of links, filenames, and usernames.
	method : str
		Defines the method used to scrape from user pages. Can be
		'ytdlp' or 'html'. Defaults to 'html' if the string doesn't
		equal 'ytdlp'.
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	
	Returns
	-------
	tuple - set of str, set of str, set of str:
		All of the links that were scraped from the given inputs, and
		then all of the usernames that were detected in `inputs`
		directly (i.e. not in links, but in the list, or in non-HTML
		files). Finally, a set of all the files that were HTML scripts.
	"""

	if method == 'ytdlp':
		with TiktokDL(stream) as ydl:
			return __process_inputs_internal(inputs, ydl, stream)
	else:
		return __process_inputs_internal(inputs, None, stream)

def update_history(filepath: str, new_users: set[str],
	stream: TextIOBase = stdout) -> None:
	"""Updates a username history file with more users.
	
	Parameters
	----------
	filepath : str
		The path leading to the history file to update
	new_users : set[str]
		The set of users to add to the file.
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	"""

	# First, load history file and read current [valid] users.
	history = set()
	try:
		with open(filepath, encoding="UTF-8") as history_file:
			lines = history_file.readlines()
			for line in lines:
				user = common.clean_up_username(line)
				if common.username_is_valid(user):
					history.add(user)
	except FileNotFoundError:
		common.notice(f"Writing to new history file {filepath}.", stream)
	# Then, inject the new users and write all of it to the file, getting rid
	# of invalid users in the process.
	history = history.union(new_users)
	with open(options.history, mode="w", encoding="UTF-8") as history_file:
		for user in history:
			history_file.write(user + "\n")

__process_inputs = process_inputs

def go_into_user_folder(user: str, stream: TextIOBase=stdout) -> bool:
	"""Creates a new user folder if required, then `cd`s into it."""

	if not os.path.isdir(user):
		try:
			os.mkdir("./" + user)
		except OSError:
			common.notice(f"Could not create new user folder \"{user}\": "
				"downloading into root folder instead.", stream)
			return False
	os.chdir("./" + user)
	return True

def download_st(original_links: set[str], folder: os.path=".",
	stream: TextIOBase=stdout):
	"""Downloads a set of links into a given folder.
	
	Note that new folders will be created for each user within the given
	folder.
	
	Parameters
	----------
	links : set of str
		The set of links to download.
	folder : os.path
		The folder to download videos into.
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	
	Returns
	-------
	tuple : list[str]
		1. A list of links that failed to download.
	"""

	links = deepcopy(original_links)
	old_cwd = os.getcwd()
	try:
		with TiktokDL(stream) as ydl:
			reattempt_bad_links = True
			while len(links) > 0:
				bad_links = set()
				for (i, link) in enumerate(links):
					link = common.clean_up_link(link)
					if common.link_is_valid(link):
						user = common.extract_username_from_link(link)
						# Username will be cleaned up once I make it a class.
						# Right now, I know it should be fine to just use it
						# straight away, but it's not the best code.
						go_back_to_root = go_into_user_folder(user, stream)
						common.notice(f"({i+1}/{len(links)}) Downloading {link}.",
							stream)
						try:
							ydl.download(link)
						except (DownloadError, ExtractorError):
							bad_links.add(link)
						finally:
							if go_back_to_root:
								os.chdir("./..")
					else:
						common.notice(f"({i+1}/{len(links)}) Link {link} is "
							"invalid!", stream)
				links = set()
				links.update(bad_links)
				if reattempt_bad_links:
					reattempt_bad_links = False
				else:
					break # `links` now has a set of errored links.
		return (links,)
	except Exception as err:
		# Re-raise all exceptions.
		raise err
	finally:
		# Always make sure to revert back to the old CWD.
		os.chdir(old_cwd)

def download_mt(links: set[str], folder: os.path=".", threads: int=1,
	stream: TextIOBase = stdout):
	"""Downloads a set of links into a given folder.
	
	Note that new folders will be created for each user within the given
	folder.
	
	Parameters
	----------
	links : set of str
		The set of links to download.
	folder : os.path
		The folder to download videos into.
	threads : int
		The number of threads to use. Defaults to 1.
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	
	Raises
	------
	ValueError
		If `threads` is < 1.
	"""

	if threads < 1:
		raise ValueError()
	elif threads == 1:
		return download_st(links, folder, stream)
	else:
		split_links = array_split(list(links), threads)
		daemons = []
		for (i, link_list) in enumerate(split_links):
			daemons.append(Thread(target=download_st, daemon=True,
				args=(set(link_list), folder, None)))
			daemons[-1].start()
		# Block until all threads have finished.
		for daemon in daemons:
			daemon.join()
		# ... will need to change the way I run threads. Will need to choose a
		# different approach that easily lets me retrieve the return value of
		# download_st() for each thread and then combine them.

if __name__ == "__main__":
	try:
		common.check_python_version()
		options = common.check_and_parse_arguments(argument_parser())

		if options.help:
			common.print_pages(common.create_pages(__doc__))
		else:
			config = t.load_or_create_config(options.config)
			if options.delete_after is not None:
				options.input.extend(options.delete_after)
			(links, users, html_files) = \
				process_inputs(options.input, options.user_method)
			if not options.no_history:
				try:
					update_history(options.history, users)
				except (FileNotFoundError, OSError):
					common.notice("Could not update the username history file "
						f"\"{options.history}\".")
					common.notice(f"The provided usernames were {users}.")
			if options.ignore is not None:
				for link in options.ignore:
					try:
						links.remove(common.clean_up_link(link))
					except KeyError:
						pass
			if options.list is not None:
				# List instead of download.
				try:
					with open(options.list, mode='w', encoding='UTF-8') as txt:
						for link in links:
							txt.write(link + '\n')
				except OSError:
					msg = f"Failed to write links to \"{options.list}\"."
					if options.delete_after is not None:
						msg += " Will not delete any input files."
					common.notice(msg)
					raise t.ConfigError()
			else:
				# Download!
				failed_links = download_mt(options.list, threads=options.split)
				print(failed_links)
			if options.delete_after is not None:
				for delete in options.delete_after:
					try:
						os.remove(delete)
					except (OSError, FileNotFoundError):
						common.notice(f"Failed to delete file \"{delete}\".")
					if delete in html_files:
						# Attempt to delete the _files folder, too.
						delete_folder = delete[:delete.rfind('.')] + "_files"
						try:
							shutil.rmtree(delete_folder)
						except (OSError, FileNotFoundError):
							common.notice("Failed to delete HTML files "
								f"folder \"{delete_folder}\".")
	except (KeyboardInterrupt, t.ConfigError):
		common.notice("Exiting...")