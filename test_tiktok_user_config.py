"""user_config Tests

Run tests on the `user_config` class in the tiktik-common module.
"""

from json import JSONDecodeError
import unittest
from unittest import TestCase
from unittest.mock import patch, mock_open
from tiktok_common import UserConfig
from test_tiktok_common import TEST_LINK, TEST_VAR_LINK

class InitTestCase(TestCase):
	def test_initialisation(self):
		config = UserConfig()
		self.assertEqual(config.config, {})

class LoadConfigTestCase(TestCase):
	def setUp(self):
		self.config = UserConfig()

	def test_no_file(self):
		with self.assertRaises(FileNotFoundError):
			self.config.load_config("")
	
	@patch("builtins.open", new_callable=mock_open, read_data="{}")
	def test_with_empty_object(self, mock_file):
		# self.assertEqual(open("./config.json").read(), "{}")
		# mock_file.assert_called_with("./config.json")
		self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"username": {{"ignore": ["{TEST_LINK}", "{TEST_LINK}"' \
		'], "notbefore": "20200505", "comment": "Hello"}}')
	def test_with_valid_object(self, mock_file):
		self.config.load_config("./config.json")
		self.assertIn("username", self.config.config)
		self.assertIn("ignore", self.config.config["username"])
		self.assertIn("notbefore", self.config.config["username"])
		self.assertIn("comment", self.config.config["username"])
		self.assertEqual(2, len(self.config.config["username"]["ignore"]))
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data='{"username": {"ignore": ["link", "link2", "notbefore": '
		'"20200505", "comment": "Hello"}}')
	def test_with_invalid_json(self, mock_file):
		with self.assertRaises(JSONDecodeError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data='{"username": {"ignore": ["link", "link2"], "notbefore": '
		'20200505, "comment": "Hello"}}')
	def test_with_invalid_notbefore(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data='{"username": {"ignore": ["link", "link2"], "notbefore": '
		'"20200505", "comment": [9]}}')
	def test_with_invalid_comment(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data='{"username": {"ignore": ["link", "link2"], "notbefore": '
		'"2020050", "comment": "Hello"}}')
	def test_with_invalid_notbefore_str(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data='{"username": {"ignore": ["1", 2], "notbefore": '
		'"20200505", "comment": "Hello"}}')
	def test_with_invalid_ignore_list(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data='{"username": {"ignore": "link", "notbefore": '
		'"20200505", "comment": "Hello"}}')
	def test_with_invalid_ignore(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data='{"username": {"ignore": ["1", 2], "notbefore": '
		'"20200505"}}')
	def test_with_missing_property(self, mock_file):
		with self.assertRaises(KeyError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"USERNAME": {{"ignore": ["{TEST_LINK}"], "notbefore": ' \
            '"12345678", "comment": "abc"}, "username": {"ignore": ["' \
            f'{TEST_LINK}", "{TEST_LINK}"], "notbefore": "20200505", ' \
            '"comment": "Hello"}}')
	def test_with_valid_object_drop_invalid_user(self, mock_file):
		self.config.load_config("./config.json")
		self.assertIn("username", self.config.config)
		self.assertNotIn("USERNAME", self.config.config)
		self.assertEqual( \
            self.config.config["username"]["notbefore"], "20200505")
		self.assertEqual(self.config.config["username"]["comment"], "Hello")
		self.assertEqual(2, len(self.config.config["username"]["ignore"]))
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"UserNAME": {{"ignore": ["{TEST_LINK}", "{TEST_LINK}"' \
		'], "notbefore": "20200505", "comment": "Hello"}}')
	def test_with_valid_object_invalid_username(self, mock_file):
		self.config.load_config("./config.json")
		self.assertIn("username", self.config.config)
		self.assertIn("ignore", self.config.config["username"])
		self.assertIn("notbefore", self.config.config["username"])
		self.assertIn("comment", self.config.config["username"])
		self.assertEqual(2, len(self.config.config["username"]["ignore"]))
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"USERNAME": {{"ignore": ["{TEST_LINK}"], "notbefore": ' \
            '"12345678", "comment": "abc"}, "userName": {"ignore": ["' \
            f'{TEST_LINK}", "{TEST_LINK}"], "notbefore": "20200505", ' \
            '"comment": "Hello"}}')
	def test_with_valid_object_drop_invalid_user(self, mock_file):
		self.config.load_config("./config.json")
		self.assertIn("username", self.config.config)

if __name__ == "__main__":
	unittest.main()