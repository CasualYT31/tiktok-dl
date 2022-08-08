"""tiktok-common Tests

Runs tests on the tiktok-common module.

IMPORTANT
---------
My mock tests aren't currently able to test if calls to `input()` print
text or not, so don't write any prompts in any `input()` calls in code
that will be tested.
"""

import unittest
from unittest.mock import patch
import io
import os
import sys
from argparse import ArgumentParser
import tiktok_common as t

class WriteTestCase(unittest.TestCase):
	def setUp(self):
		self.strstream = io.StringIO()
	
	def test_normal_use_case(self):
		t.write("abcdefg", self.strstream)
		self.assertEqual(self.strstream.getvalue(), "abcdefg\n")
	
	def test_end_parameter(self):
		t.write("abcdefg", self.strstream, '\t j\n')
		self.assertEqual(self.strstream.getvalue(), "abcdefg\t j\n")
	
	def test_no_stream(self):
		t.write("Hello", None)

class NoticeTestCase(unittest.TestCase):
	def setUp(self):
		self.strstream = io.StringIO()
	
	def test_blank_string(self):
		t.notice("", self.strstream)
		self.assertEqual(self.strstream.getvalue(), "[TIKTOK-DL] \n")

	def test_string(self):
		t.notice("Hi", self.strstream)
		self.assertEqual(self.strstream.getvalue(), "[TIKTOK-DL] Hi\n")

	def test_no_stream(self):
		t.notice("Hi", None)

class CheckPythonVersionTestCase(unittest.TestCase):
	@patch("sys.stderr", new_callable=io.StringIO)
	def test_bad_version(self, mock_print):
		with patch.object(sys, "version_info") as v_info:
			v_info.major = 3
			v_info.minor = 5
			with self.assertRaises(SystemExit):
				t.check_python_version(mock_print)
			v_info.major = 2
			v_info.minor = 0
			with self.assertRaises(SystemExit):
				t.check_python_version(mock_print)
			self.assertEqual(mock_print.getvalue(), \
				"[TIKTOK-DL] Please use Python 3.6+!\n"
				"[TIKTOK-DL] Please use Python 3.6+!\n")
	
	def test_good_version(self):
		with patch.object(sys, 'version_info') as v_info:
			v_info.major = 3
			v_info.minor = 6
			try:
				t.check_python_version()
			except SystemExit:
				self.fail("check_python_version() called sys.exit()!")
			v_info.major = 3
			v_info.minor = 10
			try:
				t.check_python_version()
			except SystemExit:
				self.fail("check_python_version() called sys.exit()!")

class CheckAndParseArgumentsTestCase(unittest.TestCase):
	def setUp(self):
		"""Creates a simple argparse.ArgumentParser object."""
		
		self.parser = ArgumentParser()
		self.parser.add_argument('dummy')
	
	@patch("sys.stderr", new_callable=io.StringIO)
	def test_no_arguments(self, mock_print):
		sys.argv = ['test']
		with self.assertRaises(SystemExit):
			t.check_and_parse_arguments(self.parser, mock_print)
		self.assertEqual(self.parser.format_help(), mock_print.getvalue())
	
	def test_arguments(self):
		sys.argv = ['test', 'input']
		try:
			options = t.check_and_parse_arguments(self.parser)
			self.assertEqual(options.dummy, "input")
		except SystemExit:
			self.fail("check_and_parse_arguments() called sys.exit()!")

class CreatePagesTestCase(unittest.TestCase):
	"""Also tests tiktok_common.comfortable_terminal_height()"""
	
	TEST_TEXT = """Lorem ipsum dolor sit amet, consectetur.
		Sed aliquam mauris quis velit commodo, eu auctor est elementum.
		Nunc eget neque eu diam maximus elementum vitae eu risus.
		Maecenas viverra risus a urna dictum accumsan.
		Fusce pharetra quam vitae dapibus tempor.
		Etiam accumsan est eget cursus iaculis.
		Nullam non dolor et risus scelerisque efficitur quis nec velit.
		Phasellus non dui sit amet eros volutpat elementum vulputate in lorem.
		Nam sed erat ut enim egestas dictum ut eget leo.
		Ut et libero sit amet erat vehicula cursus eleifend id nibh.
		Aliquam eu sapien vitae velit lobortis rutrum.
		Nullam tempus nunc vel urna gravida mollis ac non mi.
		Sed tincidunt mi eget felis bibendum, vel sodales est cursus.
		Praesent placerat nunc in lorem mollis aliquet.
		Suspendisse aliquet arcu eu arcu sodales, sit amet efficitur ipsum.
		Cras placerat neque id neque blandit aliquam.
		Donec scelerisque risus ut elit convallis, eu sodales erat posuere.
		Suspendisse aliquet arcu eu arcu sodales, sit amet efficitur ipsum.
		Suspendisse aliquet arcu eu arcu sodales, sit amet efficitur ipsum.
		Suspendisse aliquet arcu eu arcu sodales, sit amet efficitur ipsum.
		Suspendisse aliquet arcu eu arcu sodales, sit amet efficitur ipsum.
		Suspendisse aliquet arcu eu arcu sodales."""
	
	def test_blank_string(self):
		pages = t.create_pages("", 20)
		self.assertEqual(len(pages), 1)
		self.assertEqual(pages[0], "")
	
	def test_single_line_one_page(self):
		pages = t.create_pages("Hello, world!", 20)
		self.assertEqual(len(pages), 1)
		self.assertEqual(pages[0], "Hello, world!")
	
	def test_mutliple_lines_one_page(self):
		pages = t.create_pages("Hello,\nworld!", 20)
		self.assertEqual(len(pages), 1)
		self.assertEqual(pages[0], "Hello,\nworld!")
	
	def test_single_line_two_pages(self):
		pages = t.create_pages("Hello,\nworld!", 1)
		self.assertEqual(len(pages), 2)
		self.assertEqual(pages[0], "Hello,\n")
		self.assertEqual(pages[1], "world!")
	
	def test_single_line_three_pages(self):
		pages = t.create_pages("Hello,\nworld!\nIt's me again!", 1)
		self.assertEqual(len(pages), 3)
		self.assertEqual(pages[0], "Hello,\n")
		self.assertEqual(pages[1], "world!\n")
		self.assertEqual(pages[2], "It's me again!")
	
	def test_multiple_lines_three_pages(self):
		pages = t.create_pages( \
			"Pg1Ln1\nPg1Ln2\nPg2Ln1\nPg2Ln2\nPg3Ln1\nPg3Ln2", 2)
		self.assertEqual(len(pages), 3)
		self.assertEqual(pages[0], "Pg1Ln1\nPg1Ln2\n")
		self.assertEqual(pages[1], "Pg2Ln1\nPg2Ln2\n")
		self.assertEqual(pages[2], "Pg3Ln1\nPg3Ln2")
	
	def test_multiple_lines_four_pages(self):
		pages = t.create_pages( \
			"Pg1Ln1\nPg1Ln2\nPg2Ln1\nPg2Ln2\nPg3Ln1\nPg3Ln2\n", 2)
		self.assertEqual(len(pages), 4)
		self.assertEqual(pages[0], "Pg1Ln1\nPg1Ln2\n")
		self.assertEqual(pages[1], "Pg2Ln1\nPg2Ln2\n")
		self.assertEqual(pages[2], "Pg3Ln1\nPg3Ln2\n")
		self.assertEqual(pages[3], "")
	
	def test_lorem_ipsum(self):
		pages = t.create_pages(self.TEST_TEXT, 5)
		self.assertEqual(len(pages), 5)
		self.assertEqual(pages[0].count("\n"), 5)
		self.assertEqual(pages[1].count("\n"), 5)
		self.assertEqual(pages[2].count("\n"), 5)
		self.assertEqual(pages[3].count("\n"), 5)
		self.assertEqual(pages[4].count("\n"), 1)
	
	@patch("os.get_terminal_size", return_value=os.terminal_size((0, 1)))
	def test_short_terminal(self, mock):
		pages = t.create_pages(self.TEST_TEXT)
		self.assertEqual(len(pages), 1)
	
	@patch("os.get_terminal_size", return_value=os.terminal_size((0, 15)))
	def test_normal_terminal(self, mock):
		expected_page_count = -(self.TEST_TEXT.count("\n") \
			// -(t.comfortable_terminal_height()))
		pages = t.create_pages(self.TEST_TEXT)
		self.assertEqual(len(pages), expected_page_count)
	
	@patch("os.get_terminal_size", return_value=os.terminal_size((0, 100)))
	def test_large_terminal(self, mock):
		expected_page_count = -(self.TEST_TEXT.count("\n") \
			// -(t.comfortable_terminal_height()))
		pages = t.create_pages(self.TEST_TEXT)
		self.assertEqual(len(pages), expected_page_count)
	
	@patch("os.get_terminal_size", return_value=os.terminal_size((0, 100)))
	def test_negative_parameter(self, mock):
		expected_page_count = -(self.TEST_TEXT.count("\n") \
			// -(t.comfortable_terminal_height()))
		pages = t.create_pages(self.TEST_TEXT, -383)
		self.assertEqual(len(pages), expected_page_count)

class PrintPagesTestCase(unittest.TestCase):
	@patch("builtins.print")
	def test_no_pages(self, mock):
		t.print_pages([])
		mock.assert_not_called()
	
	@patch("sys.stdout", new_callable=io.StringIO)
	@patch("builtins.input", return_value="")
	def test_one_page(self, mock_input, mock_print):
		t.print_pages(["Page contents"])
		mock_input.assert_called_once()
		self.assertEqual(mock_print.getvalue(), \
			"Page contents\nPage 1 out of 1 (press enter to continue)...")
	
	@patch("sys.stdout", new_callable=io.StringIO)
	@patch("builtins.input", return_value="")
	def test_multiple_pages(self, mock_input, mock_print):
		t.print_pages(["1", "2", "3", "4", "5"])
		self.assertEqual(mock_input.call_count, 5)
		self.assertEqual(mock_print.getvalue(), \
			"1\nPage 1 out of 5 (press enter to continue)...\n" \
			"2\nPage 2 out of 5...\n3\nPage 3 out of 5...\n" \
			"4\nPage 4 out of 5...\n5\nPage 5 out of 5...")

class LoadConfigTestCase(unittest.TestCase):
	def test_no_file(self):
		with self.assertRaises(FileNotFoundError):
			t.load_config("")

if __name__ == "__main__":
	unittest.main()