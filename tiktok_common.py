"""Defines generic helper code useful for all tiktok-dl scripts.

Exports
-------
	* create_pages - Divides a chunk of text into pages.
	* print_pages - Prints strings to standard output as pages.
"""

import os

def comfortable_terminal_height():
	"""Calculates the optimal size of a page for the current terminal.
	
	Returns
	-------
	int
		`os.get_terminal_size().lines - 3`. If the value returned is <=
		0, then it can be deduced that the height of the terminal is
		"not comfortable enough."
	"""
	
	return os.get_terminal_size().lines - 3

def create_pages(lines, lines_per_page = 0):
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
	list
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

def print_pages(pages):
	"""Prints a list of strings to the console as a set of pages.
	
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
