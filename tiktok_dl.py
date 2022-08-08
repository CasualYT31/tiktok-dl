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
`tiktok-dl` accepts several different types of input. If a parameter is
given without any of the options specified from down below, the script
will treat it as input. There is an order of precedence when it comes to
determining the type of input, i.e. it will see if it is 1 first, and if
not, 2, etc.
1. Links.
	Must begin with `https://` to be recognised.
2. Filenames.
	If the given input is a valid filename, it will attempt to open it
	and read from it. This program accepts two file formats:
	- HTML
		If the file begins with `<!DOCTYPE html>`, it will be treated as
		a HTML download of a TikTok page. See the `HTML Input` section
		for more information.
	- TXT
		Otherwise, the file will be treated as a plain text file, where
		one link should be on one line.
3. Usernames.
	If the input is not a link or an existing file, the script will
	assume it's a username. It will use `yt-dlp` to scrape from a user's
	page the links to all of their videos, and feed them in as input.
	**IMPORTANT: see User Page Scraping section for more information.**

Command-Line Options
--------------------
-h
	Prints the module's docstring.
-d date
	Ensures that no video uploaded before the given date is downloaded.
	If multiple `-d` parameters are specified, the last one provided
	will be used.
-k
	By default, any HTML files provided as input are deleted after their
	links have been scraped, *including* their `_files` folder. Issue
	this argument to prevent this from happening.
-i link
	Will ensure that the given link is ignored, i.e. is removed from the
	list of links to download.
-u username
	Scrapes the newest ~30 links from the given user directly from
	TikTok using `requests_html`, and feeds them in as input.
-s [n]
	Instead of downloading any videos, all of the input links will be
	evenly divided into `n` groups and written to text files (see `-f`).
	If no `n` is provided, the user will be prompted to give the value
	when the script is run. If `0` is provided, the links will be
	downloaded instead of split.
-f filename
	Defines the filename used when writing to text files with `-s`. The
	default is `./list`. So, if `-s 3` is specified, `list0.txt`,
	`list1.txt` and `list2.txt` will be written to the current working
	directory (i.e. wherever you ran the script from).
-c filename
	Points to where the configuration script resides. By default, it
	will look for it in `./config.json`, i.e. in the current working
	directory. Please read the documentation in `tiktok_config.py` for
	more information.

User Page Scraping
------------------
Unfortunately, `yt-dlp`'s TikTok user page scraping feature has stopped
working as of July 2022. This is probably due to a change in the way
TikTok handles requests that `yt-dlp` hasn't been programmed to handle
yet. I am monitoring the situation over at
https://github.com/yt-dlp/yt-dlp/issues/3776 and will update this
project once it starts working again. In the mean time, use other
methods to scrape from user pages, such as the `-u` option, and by
providing complete HTML pages as described below.

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
"""

import sys
import tiktok_common as common

if __name__ == "__main__":
	common.check_python_version()
	
	common.print_pages(common.create_pages(__doc__))