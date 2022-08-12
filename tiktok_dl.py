"""TikTok Video Downloader Utility

As a command-line program, this script can be used to download TikTok
videos and store them in separate folders by user.

As a module, this script offers the functionality of the above whilst
allowing you to write your own scripts that work with tiktok-dl.

This script requires the following modules in order to run:
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
	TikTok using `requests_html`.
	**IMPORTANT: see User Page Scraping section for more information.**
--delete-after input
	Accepts the given parameter as input like normal. However, if the
	input is a filename, the file will be deleted after all of the
	inputted links have been processed.
--history filename
	A list of usernames that were input will be generated and will be
	appended to `./usernames.txt` by default. Use this option to append
	to a different file.
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
	* argument_parser - Constructs the tiktok-dl argument parser.
"""

from argparse import ArgumentParser, ArgumentTypeError
from concurrent.futures import thread
import tiktok_common as common
from tiktok_common import UserConfig
import tiktok_config as t

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
		default='ytdlp', metavar='METHOD')
	parser.add_argument('-d', '--delete-after', action='append', \
		metavar='FILE')
	parser.add_argument('--history', default='./usernames.txt', \
		metavar='FILEPATH')
	parser.add_argument('-n', '--no-history', action='store_true')
	parser.add_argument('-s', '--split', type=thread_count, default=1,
		metavar='THREADS')
	parser.add_argument('input', nargs='*', metavar='INPUT')
	return parser

if __name__ == "__main__":
	try:
		common.check_python_version()
		options = common.check_and_parse_arguments(argument_parser())

		if options.help:
			common.print_pages(common.create_pages(__doc__))
		else:
			config = t.load_or_create_config(options.config)
	except (KeyboardInterrupt, t.ConfigError):
		common.notice("Exiting...")