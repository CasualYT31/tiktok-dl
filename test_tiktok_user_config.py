"""user_config Tests

Run tests on the `user_config` class in the tiktik-common module.
"""

import os
from json import JSONDecodeError, dumps
import unittest
from unittest import TestCase
from unittest.mock import patch, mock_open
import builtins
from tiktok_common import UserConfig, Property, Username
from test_tiktok_common import TEST_LINK, TEST_VAR_LINK

TEST_USER_CONFIG = dumps(
	{"user1": {
	Property.NOT_BEFORE.value: "20190816",
	Property.COMMENT.value: "Hello, world!",
	Property.IGNORE.value: [TEST_LINK]
	}, "User2": {
	Property.NOT_BEFORE.value: "99998877",
	Property.COMMENT.value: "build",
	Property.IGNORE.value: []
	}}, indent=0, separators=(',', ':'))

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
		read_data=f'{{"username": {{\"{Property.IGNORE.value}\": ["{TEST_LINK}", "{TEST_LINK}"' \
		f'], \"{Property.NOT_BEFORE.value}\": "20200505", \"{Property.COMMENT.value}\": "Hello"}}}}')
	def test_with_valid_object(self, mock_file):
		self.config.load_config("./config.json")
		self.assertIn(Username("username"), self.config.config)
		self.assertIn(Property.IGNORE.value, self.config.config["username"])
		self.assertIn(Property.NOT_BEFORE.value, self.config.config["username"])
		self.assertIn(Property.COMMENT.value, self.config.config["username"])
		self.assertEqual(2, len(self.config.config["username"][Property.IGNORE.value]))
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"username": {{\"{Property.IGNORE.value}\": ["link", "link2", \"{Property.NOT_BEFORE.value}\": '
		f'"20200505", \"{Property.COMMENT.value}\": "Hello"}}}}')
	def test_with_invalid_json(self, mock_file):
		with self.assertRaises(JSONDecodeError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"username": {{\"{Property.IGNORE.value}\": ["link", "link2"], \"{Property.NOT_BEFORE.value}\": '
		f'20200505, \"{Property.COMMENT.value}\": "Hello"}}}}')
	def test_with_invalid_notbefore(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"username": {{\"{Property.IGNORE.value}\": ["link", "link2"], \"{Property.NOT_BEFORE.value}\": '
		f'"20200505", \"{Property.COMMENT.value}\": [9]}}}}')
	def test_with_invalid_comment(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"username": {{\"{Property.IGNORE.value}\": ["link", "link2"], \"{Property.NOT_BEFORE.value}\": '
		f'"2020050", \"{Property.COMMENT.value}\": "Hello"}}}}')
	def test_with_invalid_notbefore_str(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"username": {{\"{Property.IGNORE.value}\": ["1", 2], \"{Property.NOT_BEFORE.value}\": '
		f'"20200505", \"{Property.COMMENT.value}\": "Hello"}}}}')
	def test_with_invalid_ignore_list(self, mock_file):
		with self.assertRaises(ValueError):
			self.config.load_config("./config.json")
	
	# @patch("builtins.open", new_callable=mock_open, \
	# 	read_data=f'{{"username": {{\"{Property.IGNORE.value}\": "link", \"{Property.NOT_BEFORE.value}\": '
	# 	f'"20200505", \"{Property.COMMENT.value}\": "Hello"}}}}')
	# def test_with_invalid_ignore(self, mock_file):
	# 	with self.assertRaises(ValueError):
	# 		self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"username": {{\"{Property.IGNORE.value}\": ["1", 2], \"{Property.NOT_BEFORE.value}\": '
		'"20200505"}}')
	def test_with_missing_property(self, mock_file):
		with self.assertRaises(KeyError):
			self.config.load_config("./config.json")
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"USERNAME": {{\"{Property.IGNORE.value}\": ["{TEST_LINK}"], \"{Property.NOT_BEFORE.value}\": ' \
			f'"12345678", \"{Property.COMMENT.value}\": "abc"}}, "username": {{\"{Property.IGNORE.value}\": ["' \
			f'{TEST_LINK}", "{TEST_LINK}"], \"{Property.NOT_BEFORE.value}\": "20200505", ' \
			f'\"{Property.COMMENT.value}\": "Hello"}}}}')
	def test_with_valid_object_drop_invalid_user(self, mock_file):
		self.config.load_config("./config.json")
		self.assertIn("username", self.config.config)
		self.assertNotIn("USERNAME", self.config.config)
		self.assertEqual( \
			self.config.config["username"][Property.NOT_BEFORE.value], "20200505")
		self.assertEqual(self.config.config["username"][Property.COMMENT.value], "Hello")
		self.assertEqual(2, len(self.config.config["username"][Property.IGNORE.value]))
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"UserNAME": {{\"{Property.IGNORE.value}\": ["{TEST_LINK}", "{TEST_LINK}"' \
		f'], \"{Property.NOT_BEFORE.value}\": "20200505", \"{Property.COMMENT.value}\": "Hello"}}')
	def test_with_valid_object_invalid_username(self, mock_file):
		self.config.load_config("./config.json")
		self.assertIn("username", self.config.config)
		self.assertIn(Property.IGNORE.value, self.config.config["username"])
		self.assertIn(Property.NOT_BEFORE.value, self.config.config["username"])
		self.assertIn(Property.COMMENT.value, self.config.config["username"])
		self.assertEqual(2, len(self.config.config["username"][Property.IGNORE.value]))
	
	@patch("builtins.open", new_callable=mock_open, \
		read_data=f'{{"USERNAME": {{\"{Property.IGNORE.value}\": ["{TEST_LINK}"], \"{Property.NOT_BEFORE.value}\": ' \
			f'"12345678", \"{Property.COMMENT.value}\": "abc"}}, "userName": {{\"{Property.IGNORE.value}\": ["' \
			f'{TEST_LINK}", "{TEST_LINK}"], \"{Property.NOT_BEFORE.value}\": "20200505", ' \
			f'\"{Property.COMMENT.value}\": "Hello"}}}}')
	def test_with_valid_object_drop_invalid_user(self, mock_file):
		self.config.load_config("./config.json")
		self.assertIn(Username("username"), self.config.config)

class UserIsConfiguredTestCase(TestCase):
	@patch("builtins.open", new_callable=mock_open, read_data=TEST_USER_CONFIG)
	def setUp(self, mock_file):
		self.config = UserConfig()
		self.config.load_config("./config.json")
	
	def test_user_is_in_config(self):
		self.assertTrue(self.config.user_is_configured(U"user1"))
		self.assertTrue(self.config.user_is_configured(U"user2"))
		self.assertTrue(self.config.user_is_configured(U"\tUSER2 "))
	
	def test_user_is_not_in_config(self):
		self.assertFalse(self.config.user_is_configured("u"))

class NotBeforeTestCase(TestCase):
	@patch("builtins.open", new_callable=mock_open, read_data=TEST_USER_CONFIG)
	def setUp(self, mock_file):
		self.config = UserConfig()
		self.config.load_config("./config.json")
	
	def test_get_not_before(self):
		self.assertEqual(self.config.get_not_before("useR1"), "20190816")
		self.assertEqual(self.config.get_not_before("user2"), "99998877")
	
	def test_set_not_before(self):
		self.assertEqual(self.config.get_not_before("useR1"), "20190816")
		self.config.set_not_before("USER1", "\t\n\r77778899  ")
		self.assertEqual(self.config.get_not_before("User1"), "77778899")
	
	def test_set_not_before_new_user(self):
		self.assertFalse(self.config.user_is_configured("user3"))
		self.config.set_not_before("user3", "12345678")
		self.assertTrue(self.config.user_is_configured("user3"))
		self.assertEqual(self.config.get_not_before("uSer3"), "12345678")
	
	def test_not_before_invalid(self):
		with self.assertRaises(KeyError):
			self.config.get_not_before("user3")
		self.assertEqual(self.config.get_not_before("user1"), "20190816")
		with self.assertRaises(ValueError):
			self.config.set_not_before("user1", "1234567")
		self.assertEqual(self.config.get_not_before("user1"), "20190816")
		with self.assertRaises(ValueError):
			self.config.set_not_before("user3", "123456789")
		self.assertEqual(self.config.get_not_before("user1"), "20190816")
		self.assertFalse(self.config.user_is_configured("user3"))

class CommentTestCase(TestCase):
	@patch("builtins.open", new_callable=mock_open, read_data=TEST_USER_CONFIG)
	def setUp(self, mock_file):
		self.config = UserConfig()
		self.config.load_config("./config.json")
	
	def test_get_comment(self):
		self.assertEqual(self.config.get_comment("useR1"), "Hello, world!")
		self.assertEqual(self.config.get_comment("user2"), "build")
	
	def test_set_comment(self):
		self.assertEqual(self.config.get_comment("useR1"), "Hello, world!")
		self.config.set_comment("USER1", "\t\n\rHi!  ")
		self.assertEqual(self.config.get_comment("User1"), "\t\n\rHi!  ")
	
	def test_set_comment_new_user(self):
		self.assertFalse(self.config.user_is_configured("user3"))
		self.config.set_comment("user3", "12345678")
		self.assertTrue(self.config.user_is_configured("user3"))
		self.assertEqual(self.config.get_comment("uSer3"), "12345678")
	
	def test_comment_invalid(self):
		with self.assertRaises(KeyError):
			self.config.get_comment("user3")
		self.assertFalse(self.config.user_is_configured("user3"))

class IgnoreTestCase(TestCase):
	@patch("builtins.open", new_callable=mock_open, read_data=TEST_USER_CONFIG)
	def setUp(self, mock_file):
		self.config = UserConfig()
		self.config.load_config("./config.json")
	
	def test_get_ignore_links(self):
		links = self.config.get_ignore_links("uSEr1")
		self.assertEqual(len(links), 1)
		self.assertEqual(links[0], TEST_LINK)
		links = self.config.get_ignore_links("uSEr2 ")
		self.assertEqual(len(links), 0)
		with self.assertRaises(KeyError):
			self.config.get_ignore_links("user3")
	
	def test_add_ignore_links(self):
		old_links = self.config.get_ignore_links("user1")
		self.config.toggle_ignore_link("https://www.tiktok.com/@USER1/video/"
			"1234567891234567890")
		self.assertLess(len(old_links),
			len(self.config.get_ignore_links("user1")))
		self.config.toggle_ignore_link("https://www.tiktok.com/@user3/video/"
			"1234567891234567890")
		self.assertEqual(len(self.config.get_ignore_links("user3")), 1)
	
	def test_remove_ignore_links(self):
		old_links = self.config.get_ignore_links("user1")
		self.config.toggle_ignore_link(TEST_LINK)
		self.assertGreater(len(old_links),
			len(self.config.get_ignore_links("user1")))
	
	def test_remove_ignore_var_links(self):
		old_links = self.config.get_ignore_links("user1")
		self.config.toggle_ignore_link(TEST_VAR_LINK)
		self.assertGreater(len(old_links),
			len(self.config.get_ignore_links("user1")))

class SaveConfigTestCase(TestCase):
	def setUp(self):
		self._orig_pathexists = os.path.exists
		os.path.exists = True
	
	@patch("builtins.open", new_callable=mock_open)
	def test_with_empty_object(self, mock_file):
		conf = UserConfig()
		conf.save_config("File_Path")
		builtins.open.assert_called_once_with(
			"File_Path", mode='w', encoding='UTF-8')
		builtins.open.return_value.write.assert_called_once_with('{}')

if __name__ == "__main__":
	unittest.main()