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
--output filename
	When this option is given, terminal output will instead be
	redirected to the given text file, but only when downloading. For
	multi-threaded mode, there will be a file for each thread. For
	example, if 'output.txt' is given, and `-s 3` is given, then there
	will be three files called 'output0.txt', 'output1.txt', and
	'output2.txt'. Any files will be overwritten if they exist.
--user username
	When this option is given, only videos from the given user will be
	used as input. This option can be given multiple times, and will add
	usernames to the list (e.g. only videos from all the users given
	will be downloaded).
--folder path
	The folder to download videos into. Defaults to the CWD. User
	folders will be created within this directory as appropriate.
--error-links-history path
	You should provide a text file here. Defaults to "./404.txt". If any
	links fail due to a 404 HTTP error, they will be appended to the
	given text file, one link per line.
--retries count
	The number of times to retry failed links. Defaults to 3 times.
	Links that fail due to 404 errors do not count and are never
	retried.
--count-links-from-html
	If you specify this option, and you also provide HTML scripts,
	before downloading/listing begins, the number of links that were
	scraped from each provided script will be printed to the console.
	You are then given the option to continue with the operation by
	pressing enter, or cancelling it by issuing Ctrl+C.

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

Update: I'm now seemingly unable to download user pages in this way. Up
to now I've had to deal with using a line of JavaScript written by
someone else to achieve a similar result.

Exports
-------
	* YtDlpLogger - Logger class to redirect `yt-dlp` output.
	* TiktokDL - A `YoutubeDL` object with a custom logger.
	* thread_count - The type of argument that --split is.
	* retry_count - The type of argument that --retries is.
	* argument_parser - Constructs the tiktok-dl argument parser.
	* scrape_from_user - Scrape links from a TikTok user's page.
	* scrape_from_file - Processes inputs from files.
	* process_inputs - Finds all the links in the given list of inputs.
	* update_history - Updates a username history file with more users.
	* video_folder - Creates a user's folder and returns its path.
	* download_st - Download a set of links in the main thread.
	* DownloadStThread - A `Thread` that runs `download_st` separately.
	* download_mt - Download a set of links across multiple threads.
"""

from platform import system
import os
import re
import shutil
from collections import Counter
from typing import Callable
from threading import Thread
from time import sleep
from copy import deepcopy
from sys import stdout
from io import TextIOBase
from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError
from yt_dlp import YoutubeDL, DateRange
from yt_dlp.utils import DownloadError, ExtractorError
from urllib.error import HTTPError
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

def retry_count(value):
    ivalue = int(value)
    if ivalue < 0:
        raise ArgumentTypeError(f"{value} is an invalid retry number, must "
			"be >= 0")
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
	parser.add_argument('--user-method', choices=['ytdlp', 'html'], \
		default=DEFAULT_USER_METHOD, metavar='METHOD')
	parser.add_argument('-d', '--delete-after', action='append', \
		metavar='FILE')
	parser.add_argument('--history', default='./usernames.txt', \
		metavar='FILEPATH')
	parser.add_argument('-n', '--no-history', action='store_true')
	parser.add_argument('-s', '--split', type=thread_count, default=1,
		metavar='THREADS')
	parser.add_argument('-o', '--output', metavar='FILEPATH')
	parser.add_argument('-u', '--user', action='append', metavar='USERNAME')
	parser.add_argument('-f', '--folder', default='.', metavar='OUTPUTFOLDER')
	parser.add_argument('-e', '--error-links-history', default='./404.txt', \
		metavar='FILEPATH')
	parser.add_argument('-r', '--retries', type=retry_count, default=3, \
		metavar='RETRIES')
	parser.add_argument('--count-links-from-html', action='store_true')
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

def __process_inputs__(inputs, whitelist, user_method, stream):
	"""Internal function: use process_inputs instead!

	Used to forward declare the process_input function so that scrape_from_file
	can call it.
	"""

	pass
__process_inputs = __process_inputs__

def scrape_from_file(path: str, whitelist: set[str], session: YoutubeDL=None,
	stream: TextIOBase = stdout) -> tuple[set[str],set[str],set[str],dict]:
	"""Scrapes inputs from a given file.

	If the given file is determined to be an HTML script, the links will
	be scraped and returned. Otherwise, the file is treated as a text
	file, where each line represents one input that is passed to
	`process_inputs`.
	
	Parameters
	----------
	path : str
		Path to the file to read from.
	whitelist : set of str
		If a link is for a video uploaded by a user not in this list,
		then it will be removed from the resulting tuple. If the
		whitelist is blank, then no links will be removed from the
		result. By default, the whitelist is blank.
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
		return set(), set(), set(), {}
	elif contents[0] == "<!DOCTYPE html>":
		links = set()
		count = {path: 0}
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
					count[path] = count[path] + 1
		return links, set(), set([path]), count
	else:
		# Before passing it to process_inputs, remove any instances of "path"
		# in the file to prevent RecursionErrors. Also remove blank lines.
		contents = [line for line in contents \
			if line != "" and not common.the_same_filepath(path, line)]
		return __process_inputs(contents, whitelist, session, stream)

def __process_inputs_internal(inputs, whitelist, session, stream):
	links = set()
	users = set()
	htmls = set()
	html_counts = {}
	for input in inputs:
		if common.link_is_valid(common.clean_up_link(input)):
			links.add(common.clean_up_link(input))
		elif Path(input).is_file():
			(new_links, new_users, new_htmls, new_html_counts) = \
				scrape_from_file(input, whitelist, session, stream)
			links = links.union(new_links)
			users = users.union(new_users)
			htmls = htmls.union(new_htmls)
			html_counts = html_counts | new_html_counts
		elif common.username_is_valid(common.clean_up_username(input)):
			links = links.union(scrape_from_user(input, session, stream))
			users.add(common.clean_up_username(input))
		else:
			common.notice(f"Invalid input: {input}", stream)
	return (links, users, htmls, html_counts)

def process_inputs(inputs: list[str], whitelist: set[str]=set(),
	method: str=DEFAULT_USER_METHOD,
	stream: TextIOBase = stdout) -> \
	tuple[set[str],set[str],set[str],dict]:
	"""Scrapes all of the links from a given list of inputs.
	
	Parameters
	----------
	inputs : list of str
		List of links, filenames, and usernames
	whitelist : set of str
		If a link is for a video uploaded by a user not in this list,
		then it will be removed from the resulting tuple. If the
		whitelist is blank, then no links will be removed from the
		result. By default, the whitelist is blank.
	method : str
		Defines the method used to scrape from user pages. Can be
		'ytdlp' or 'html'. Defaults to 'html' if the string doesn't
		equal 'ytdlp'.
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	
	Returns
	-------
	tuple - set of str, set of str, set of str, dict:
		All of the links that were scraped from the given inputs, and
		then all of the usernames that were detected in `inputs` (both
		directly in the list, as well as in links). Then, a set of all
		the files that were HTML scripts, and finally, a dictionary,
		where each key is a HTML script path as given in the parameters,
		and each value is the number of links extracted from the
		corresponding HTML script.
	"""

	ret = None
	if method == 'ytdlp':
		with TiktokDL(stream) as ydl:
			ret = __process_inputs_internal(inputs, whitelist, ydl, stream)
	else:
		ret = __process_inputs_internal(inputs, whitelist, None, stream)
	# Now remove all links from users that aren't in the whitelist.
	# You could probably use a set comprehension here but idc.
	if len(whitelist) > 0:
		old_links = deepcopy(ret[0])
		for link in old_links:
			for user in whitelist:
				if common.extract_username_from_link(link) != user:
					ret[0].remove(link)
	# Now, update the user set with all the usernames found in the links allowed.
	for link in ret[0]:
		ret[1].add(common.extract_username_from_link(link))
	return ret

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

def video_folder(folder: str, user: str, stream: TextIOBase=stdout) -> bool:
	"""Creates a new user folder if required, then returns the path to
	it.

	Parameters
	----------
	folder : str
		The folder to create the user folder within.
	user : str
		The name of the user to create the folder for. This is cleaned
		up before processing.
	stream : TextIOBase
		The stream to output error information to. Defaults to `stdout`.
	
	Returns
	-------
	The folder to download the user's videos into. A blank string will
	be returned if the user folder couldn't be found or created.
	"""

	user = common.clean_up_username(user)
	try:
		os.makedirs(folder + "/" + user, exist_ok=True)
	except OSError:
		common.notice(f"Could not create new user folder \"{user}\": "
			"downloading into root folder instead.", stream)
		return folder
	return folder + "/" + user

def download_st(original_links: set[str], folder: os.path=".",
	retries: int=2, user_config: UserConfig=None, stream: TextIOBase=stdout,
	progress_func: Callable[[int, int, bool, bool], None]=None):
	"""Downloads a set of links into a given folder.
	
	Note that new folders will be created for each user within the given
	folder.
	
	Parameters
	----------
	links : set of str
		The set of links to download.
	folder : os.path
		The folder to download videos into.
	retries : int
		The number of times to retry failed (non-404) links. Defaults to
		2.
	user_config : UserConfig
		The configurations for each user. `None` means that there are no
		extra configurations (default).
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	progress_func : Callable[[int, int, bool, bool], None]
		The function to invoke when this function needs to report
		that it has completed a link. If `None`, no progress will be
		reported. See `DownloadStThread` for more information.
	
	Returns
	-------
	tuple : set[str], set[str]
		1. A set of links that failed to download.
		2. A set of links that failed due to a 404 error.
	
	Raises
	------
	ValueError
		If `retries` < 0.
	"""

	if (retries < 0):
		raise ValueError
	links = deepcopy(original_links)
	http_404_links = set()
	try:
		old_len_of_links = len(links)
		for attempt in range(retries + 1):
			bad_links = set()
			old_len_of_links = len(links)
			for (i, link) in enumerate(links):
				if progress_func is not None:
					progress_func(i, len(links), attempt == 0, False)
				link = common.clean_up_link(link)
				if common.link_is_valid(link):
					if user_config is not None and \
						user_config.is_ignored_link(link):
						common.notice(f"({i+1}/{len(links)}) Link {link} is to be "
							"ignored.", stream)
					else:
						user = common.extract_username_from_link(link)
						# Username will be cleaned up once I make it a class.
						# Right now, I know it should be fine to just use it
						# straight away, but it's not the best code.
						common.notice(f"({i+1}/{len(links)}) Downloading {link}.",
							stream)
						ytdlp_opts = {
							"outtmpl": f"{video_folder(folder, user, stream)}"
							"/%(title).175s [%(id)s].%(ext)s"
							}
						try:
							notbefore = user_config.get_not_before(user)
							if notbefore != "":
								ytdlp_opts['daterange'] = DateRange(start=notbefore)
						except KeyError:
							pass
						with TiktokDL(stream, ytdlp_opts) as ydl:
							try:
								ydl.download(link)
							except (DownloadError, ExtractorError) as err:
								if isinstance(err.exc_info[1], HTTPError):
									if err.exc_info[1].code == 404:
										# Unavailable video, so no point trying to
										# download it again. It's worth reporting
										# it, though, because sometimes the video
										# might be available but inaccesible via
										# yt-dlp.
										http_404_links.add(link)
								else:
									bad_links.add(link)
				else:
					common.notice(f"({i+1}/{len(links)}) Link {link} is "
						"invalid!", stream)
			if progress_func is not None:
				progress_func(len(links), len(links), attempt == 0, False)
			links = set()
			links.update(bad_links)
			if len(links) == 0:
				break
		if progress_func is not None:
			progress_func(old_len_of_links, old_len_of_links, False, True)
		return (links, http_404_links)
	except Exception as err:
		# Re-raise all exceptions.
		if progress_func is not None:
			progress_func(0, 0, False, True)
		raise err

class DownloadStThread(Thread):
	"""Allows client code to run `download_st` in a separate thread.
	"""

	def __init__(self, links: set[str], folder: os.path=".",
		file: str=None, retries: int=2, user_config: UserConfig=None):
		"""Sets up a `download_st` thread, ready for execution later.

		Note that a threaded version of `download_st` cannot output
		anything to a stream.
		
		Parameters
		----------
		links : set of str
			The set of links to download.
		folder : os.path
			The folder to download videos into.
		file : str
			The path of the file to write output to.
		retries : int
			The number of times to try to download failed links.
		user_config : UserConfig
			The configurations for each user. Default is `None`.
		"""

		Thread.__init__(self)
		self.daemon = True
		self.result = None
		self.links = links
		self.folder = folder
		self.retries = retries
		self.user_config = user_config
		self.progress = (0, 0, True, False)
		if file is None:
			self.stream = None
		else:
			self.stream = open(file, mode='w', encoding='utf-8')
	
	def __del__(self):
		"""Closes the file stream used to store output.
		"""

		if self.stream is not None:
			self.stream.close()

	def run(self):
		"""Executes the `download_st` call and stores the result in
		`self.result`.
		"""

		self.result = download_st(self.links, self.folder, self.retries,
			self.user_config, self.stream, self.progress_report)
	
	def progress_report(self, progress: int, total: int, first_call: bool,
		completed: bool) -> None:
		"""Report on the progress of the thread.

		Updates `self.progress` with a tuple. The first int holds the
		number of links processed so far, and the second int holds the
		total number of links to process. The third value, a bool, is
		`False` if the progress report describes a reattempt to download
		failed links. And the final value, another bool, is `True` once
		the thread has completed its work.
		
		Parameters
		----------
		progress : int
			The number of links processed so far.
		total : int
			The total number of links to process.
		first_call : bool
			Should be `False` if the progress report is describing a
			reattempt to download failed links.
		completed : bool
			`True` if all the links have been processed or if there was
			an error, `False` if the thread is still completing work.
		"""

		self.progress = (progress, total, first_call, completed)

def download_mt(links: set[str], folder: os.path=".", threads: int=1,
	file: str=None, retries: int=2, user_config: UserConfig=None,
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
	threads : int
		The number of threads to use. Defaults to 1.
	file : str
		If this argument is given, a set of text files will be created
		and output will be redirected into there. This overrides
		`stream` if given.
	retries : int
		The number of times to try downloaded failed links.
	user_config : UserConfig
		The configurations for each user. If `None`, no extra
		configurations will be considered (this is the default).
	stream : io.TextIOBase
		The stream to print messages to. Defaults to `sys.stdout`. Can
		be `None`.
	
	Returns
	tuple : set[str], set[str]
		1. A set of links that failed to download.
		2. A set of links that failed due to a 404 error.
	
	Raises
	------
	ValueError
		If `threads` is < 1 or `retries` < 0.
	"""

	if threads < 1:
		raise ValueError()
	elif threads == 1:
		if file is None:
			return download_st(links, folder, retries, user_config, stream)
		else:
			with open(file, mode='w', encoding='utf-8') as outputStream:
				return download_st(links, folder, retries, user_config,
					outputStream)
	else:
		split_links = array_split(list(links), threads)
		# If any of the lists are empty, remove them.
		split_links = [l for l in split_links if len(l) > 0]
		running_threads = []
		for (i, link_list) in enumerate(split_links):
			if file is None:
				running_threads.append(DownloadStThread(set(link_list), folder,
					retries=retries, user_config=user_config))
			else:
				if '.' in file:
					running_threads.append(DownloadStThread(set(link_list), folder,
						file[:file.rfind('.')] + str(i) +
						file[file.rfind('.'):], retries=retries,
						user_config=user_config))
				else:
					running_threads.append(DownloadStThread(set(link_list), folder,
						file + str(i), retries=retries, user_config=user_config))
			running_threads[-1].start()
		number_of_digits = None
		while True:
			progress_reports = []
			for thread in running_threads:
				progress_reports.append(thread.progress)
			for report in progress_reports:
				if number_of_digits is None:
					# Due to the way the array_split function works, accessing the
					# first thread's total link count and using that for the digit
					# count will always make sure that the highest digit count is
					# used, to ensure that every line is the same length regardless
					# of each thread's individual total link count.
					number_of_digits = len(str(report[1]))
				current = f"{{:0{number_of_digits}}}".format(report[0])
				total_str = f"{{:0{number_of_digits}}}".format(report[1])
				if report[3] is True:
					# Thread has completed, so skip its progress bar and leave it
					# at 100%.
					common.print_progress_bar(
						iteration=100,
						total=100,
						prefix=f"\033[92m{current} of {total_str}",
						suffix=" \033[0m",
						decimals=0,
						printEnd='\r\n',
						stream=stream)
				elif report[2] is False:
					# Display progress bar with different colour for failed links.
					common.print_progress_bar(
						iteration=report[0],
						total=report[1],
						prefix=f"\033[93m{current} of {total_str}",
						suffix=" \033[0m",
						decimals=0,
						printEnd='\r\n',
						stream=stream)
				else:
					common.print_progress_bar(
						iteration=report[0],
						total=report[1],
						prefix=f"{current} of {total_str}",
						decimals=0,
						printEnd='\r\n',
						stream=stream)
			if all([i[3] for i in progress_reports]) is False:
			# 	# Go back to the beginning of the first progress bar line.
			# 	for i in range(len(running_threads)):
			# 		print("\033[A", end='')
				# This stopped fucking working, so I'm just resorting to using os.
				# It's something to do with download_st() now opening a new
				# YoutubeDL() instance for every link, because once I comment the
				# whole with statement out, the progress bars work properly. If
				# there's some way to change outtmpl after YoutubeDL has been
				# created, then I will try bringing back the old method, but for
				# now, put up with this.
				sleep(0.5)
				if "Windows" in system():
					os.system('cls')
				else:
					os.system('clear')
			else:
				break
		failed_links = set()
		failed_links_404 = set()
		for thread_index, thread in enumerate(running_threads):
			thread.join()
			# In very rare cases, thread.result can be None. Not sure why yet. For
			# now, just report it to the user whenever it happens, and don't update
			# the sets.
			if thread.result is None:
				print("Thread " + str(thread_index) + " did not have a result "
					"tuple! The links it was given:")
				print(*thread.links, sep='\n')
			else:
				failed_links.update(thread.result[0])
				failed_links_404.update(thread.result[1])
		return (failed_links, failed_links_404)

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
			if options.user is None:
				options.user = []
			(links, users, html_files, no_of_links_from_html_files) = \
				process_inputs(options.input, set(options.user),
				options.user_method)
			if options.count_links_from_html and \
				len(no_of_links_from_html_files) > 0:
				for path, count in no_of_links_from_html_files.items():
					common.notice(f"HTML script {path} has {count} link"
						f"{'' if count == 1 else 's'}.")
				common.notice("Press ENTER to continue or Ctrl+C to cancel.")
				input()
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
			# Now, do something with the links.
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
				results = download_mt(links, threads=options.split,
					file=options.output, folder=options.folder,
					retries=options.retries, user_config=config)
				# Please see Issue #5 {
				number_of_bad_links = len(results[0]) + len(results[1])
				if number_of_bad_links > 0:
					try:
						with open(options.error_links_history, mode='a',
							encoding='utf-8') as errored_links:
							for link in results[0]:
								errored_links.write(link + "\n")
							for link in results[1]:
								errored_links.write(link + "\n")
						common.notice(f"Wrote {number_of_bad_links} bad link"
							f"{'' if number_of_bad_links == 1 else 's'} to "
							f"{options.error_links_history}.")
					except OSError:
						common.notice("Could not write bad link"
							f"{'' if number_of_bad_links == 1 else 's'} to "
							f"{options.error_links_history}, outputting to console "
							f"instead: {' '.join(map(str, results[0]))} "
							f"{' '.join(map(str, results[1]))}")
				# }
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
