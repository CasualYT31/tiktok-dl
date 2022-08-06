"""tiktok-dl Configuration Editor

As a command-line program, this script can be used to view and amend
tiktok-dl configuration files, either via arguments or via an
interactive prompt.

As a module, this script offers the functionality of the above whilst
allowing you to write your own scripts that work with tiktok-dl config
files.
"""

if __name__ == "__main__":
	# Python version checking.
	if sys.version_info < (3,6):
		print("Please use Python 3.6+!")
		sys.exit()