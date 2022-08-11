"""tiktok-config Tests

Run tests on the tiktok-config module. Best to run this suite with `-b`.
"""

import unittest
from unittest.mock import patch, mock_open
import io
from argparse import ArgumentError
import tiktok_config as t
from test_tiktok_common import TEST_LINK

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
	
	def test_config(self):
		options = self.parser.parse_args([''])
		self.assertEqual(options.config, "./config.json")
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['-c'])
		options = self.parser.parse_args(['-c', 'path.json'])
		self.assertEqual(options.config, "path.json")
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['--config', 'path.json', '-c'])
		options = self.parser.parse_args(['-c', 'path.json', '--config', '2'])
		self.assertEqual(options.config, "2")
	
	def test_interactive(self):
		options = self.parser.parse_args([''])
		self.assertFalse(options.interactive)
		options = self.parser.parse_args(['--interactive'])
		self.assertTrue(options.interactive)
		options = self.parser.parse_args(['--in'])
		self.assertTrue(options.interactive)
		with self.assertRaises(SystemExit):
			self.parser.parse_args(['--i'])
	
	def test_positional(self):
		options = self.parser.parse_args(['user1', 'user2', '--list', 'p'])
		self.assertEqual(len(options.user), 2)
		options = self.parser.parse_args(['--list', 'p'])
		self.assertEqual(len(options.user), 0)

class LoadOrCreateConfigTestCase(unittest.TestCase):
	def test_non_existent_file(self):
		str_stream = io.StringIO()
		config = t.load_or_create_config("", str_stream)
		self.assertEqual(config.config, {})
		self.assertIn( \
			"Will create new configuration script at \"\".", \
			str_stream.getvalue())
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"username": {{"ignore": ["{TEST_LINK}", "'
		f'{TEST_LINK}"], "notbefore": "20200505", "comment": "Hello"}}}}')
	def test_with_valid_object(self, mock_file):
		config = t.load_or_create_config("./config.json")
		self.assertIn("username", config.config)
		self.assertIn("ignore", config.config["username"])
		self.assertIn("notbefore", config.config["username"])
		self.assertIn("comment", config.config["username"])
		self.assertEqual(2, len(config.config["username"]["ignore"]))

class PerformSetsTestCase(unittest.TestCase):
	def setUp(self):
		# Setup configuration object here.
		pass

if __name__ == "__main__":
	unittest.main()