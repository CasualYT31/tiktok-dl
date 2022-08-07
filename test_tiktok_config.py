"""tiktok-config Tests

Run tests on the tiktok-config module. Best to run this suite with `-b`.
"""

import unittest
from unittest.mock import patch
import io
from argparse import ArgumentError
import tiktok_config as t

class ArgumentParserTestCase(unittest.TestCase):
	def setUp(self):
		self.parser = t.argument_parser()
	
	def test_help(self):
		options = self.parser.parse_args([''])
		self.assertFalse(options.help)
		options = self.parser.parse_args(['-h'])
		self.assertTrue(options.help)
		options = self.parser.parse_args(['--help'])
		self.assertTrue(options.help)
	
	@patch("sys.stdout", new_callable=io.StringIO)
	def test_version(self, mock_print):
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['-v'])
		self.assertEqual(mock_print.getvalue(), \
			t.common.version_string() + "\n")
	
	def test_set(self):
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['-s'])
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['-s', 'p1'])
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['-s', 'p1', 'p2'])
		options = self.parser.parse_args(['-s', 'p1', 'p2', 'p3'])
		self.assertEqual(len(options.set), 1)
		options = self.parser.parse_args( \
			['--set', 'p1', 'p2', 'p3', '-s', 'p1', 'p2', 'p3'])
		self.assertEqual(len(options.set), 2)
	
	def test_ignore(self):
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['-i'])
		options = self.parser.parse_args(['-i', 'link'])
		self.assertEqual(len(options.ignore), 1)
		options = self.parser.parse_args(['-i', 'link', '--ignore', 'link2'])
		self.assertEqual(len(options.ignore), 2)
	
	def test_delete(self):
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['-d'])
		options = self.parser.parse_args(['-d', 'link'])
		self.assertEqual(len(options.delete), 1)
		options = self.parser.parse_args(['-d', 'link', '--delete', 'link2'])
		self.assertEqual(len(options.delete), 2)
	
	def test_list(self):
		options = self.parser.parse_args([''])
		self.assertEqual(options.list, None)
		options = self.parser.parse_args(['-l'])
		self.assertEqual(options.list, '.*')
		options = self.parser.parse_args(['-l', 'a?b*c+.'])
		self.assertEqual(options.list, 'a?b*c+.')
		options = self.parser.parse_args(['-l', 'a?b*c+.', '-l'])
		self.assertEqual(options.list, '.*')
		options = self.parser.parse_args( \
			['-l', 'a?b*c+.', '-l', '--list', '?'])
		self.assertEqual(options.list, '?')
	
	def test_positional(self):
		options = self.parser.parse_args(['user1', 'user2', '--list', 'p'])
		self.assertEqual(len(options.user), 2)
		options = self.parser.parse_args(['--list', 'p'])
		self.assertEqual(len(options.user), 0)

if __name__ == "__main__":
	unittest.main()