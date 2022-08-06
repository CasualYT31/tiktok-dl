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
	Prints the module's docstring.
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
	Lists all the users who have configuration objects. The optional
	filter is a regular expression that must fully match with a username
	before it can be displayed.
"""

import argparse
import tiktok_common as common

if __name__ == "__main__":
	common.check_python_version()
	
	parser = argparse.ArgumentParser(description=")