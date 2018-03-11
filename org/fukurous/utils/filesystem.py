#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for file-system.

This module includes unit test suite for itself.
Please execute following command on your shell.

$ python filesystem.py

If you need more information for test result, execute it with '--verbose'.
"""

__author__    = 'MIYAZAKI Masafumi (The Project Fukurous)'
__date__      = '2017/04/09'
__version__   = '0.0.2'

__copyright__ = "Copyright 2017 MIYAZAKI Masafumi (The Project Fukurous)"
__license__   = 'The 2-Clause BSD License'


import copy
import os
from pathlib import Path
import tempfile
import unittest


class TestFilesystem(unittest.TestCase):
	""" Test suite for filesystem """

	def test_case_01(self):
		""" Test case for filelist_with_pattern, filelist, filelist_recursive, FileTree """

		# Create following file tree for testing.
		#  root
		#   + aaaa        ... directory
		#   + bbbb.txt    ... file
		#   + cccc        ... directory
		#   |  + dddd.txt ... file
		#   + eeee.txt    ... file

		with tempfile.TemporaryDirectory() as temp_directory:
			root = Path(temp_directory)
			aaaa = (root / 'aaaa')
			aaaa.mkdir()
			bbbb = (root / 'bbbb.txt')
			bbbb.touch()
			cccc = (root / 'cccc')
			cccc.mkdir()
			dddd = (cccc / 'dddd.txt')
			dddd.touch()
			eeee = (root / 'eeee.txt')
			eeee.touch()

			a_list = list(map(lambda each: each.name, filelist_with_pattern(temp_directory, '**/*.txt')))
			a_list.sort()
			self.assertEqual(a_list, ['bbbb.txt', 'dddd.txt', 'eeee.txt'])

			a_list = list(map(lambda each: each.name, filelist(temp_directory)))
			a_list.sort()
			self.assertEqual(a_list, ['aaaa', 'bbbb.txt', 'cccc', 'eeee.txt'])

			a_list = list(map(lambda each: each.name, filelist(temp_directory, recursive = True)))
			a_list.sort()
			self.assertEqual(a_list, ['aaaa', 'bbbb.txt', 'cccc', 'dddd.txt', 'eeee.txt'])

			the_list = list(map(lambda each: each.name, filelist_recursive(temp_directory)))
			the_list.sort()
			self.assertEqual(a_list, the_list)

			a_tree = FileTree(filelist_recursive(temp_directory))
			expected_tree = os.linesep.join([
				str(root),
				' + aaaa',
				' + bbbb.txt',
				' + cccc',
				' | L dddd.txt',
				' L eeee.txt',
				''])
			self.assertEqual(str(a_tree), expected_tree)

			new_filelist = [
				Path('/a/b/c'),
				Path('/a/b/c/d'),
				Path('/a/b/e'),
				Path('/a/b/f'),
				Path('/a/b/f/g')]
			a_tree.set(new_filelist)
			expected_tree = os.linesep.join([
				'/a/b',
				' + c',
				' | L d',
				' + e',
				' L f',
				'   L g',
				''])
			self.assertEqual(str(a_tree), expected_tree)


def filelist_with_pattern(the_path, the_pattern):
	""" Create a filelist on the_path with the_pattern. """
	directory = Path(the_path)
	return list(directory.glob(the_pattern))

def filelist(the_path, recursive = False):
	""" Create a filelist on the_path. """
	directory = Path(the_path)

	if recursive is True:
		pattern = '**/*'
	else:
		pattern = '*'

	return filelist_with_pattern(the_path, pattern)

def filelist_recursive(the_path):
	""" Create a filelist on the_path recursively. """
	return filelist(the_path, recursive = True)


class FileTree(object):
	""" Object for a filetree. """ 

	def __init__(self, filelist = None):
		self._filelist = filelist
		self._filetree = None
		self._need_to_generate = True
		self.newline = os.linesep
		self.space = ' '
		self.margin_empty = ' '
		self.margin_pass = '|'
		self.margin_branch = '+'
		self.margin_end = 'L'

	def __str__(self):
		""" The filetree as string. """
		if self._need_to_generate is True:
			self._generate()
			self._need_to_generate = False

		return self._filetree

	def invalidate(self):
		""" Invalidate the filelist. """
		self._filetree = None
		self._need_to_generate = True

	def set(self, the_filelist):
		""" Set the_filelist as the filelist. """
		self._filelist = the_filelist
		self.invalidate()

	def _generate(self):
		""" Generate a filetree from the filelist. """
		self._filelist.sort(key = lambda each: str(each))
		parts_list = list(map(lambda each: list(each.parts), self._filelist))
		parts_list.insert(0, parts_list[0][0:len(parts_list[0]) - 1])
		parts_list.reverse()
		parts_list = [[]] + parts_list + [[]]

		tree_list = []

		for row in range(1, len(parts_list) - 1):
			(previous_row, current_row, next_row) = parts_list[row-1:row+2]
			new_row = current_row.copy()
			for col in reversed(range(1, len(current_row) - 1)):
				if current_row[0:col+1] == next_row[0:col+1]:
					if (len(previous_row) > col) and (current_row[col] == previous_row[col]):
						new_row[col] = self.margin_branch
					else:
						new_row[col] = self.margin_end
					if col > 0:
						col = col - 1
						while col >= 0:
							if (len(previous_row) > col) and (current_row[col] == previous_row[col]):
								new_row[col] = self.margin_pass
							else:
								new_row[col] = self.margin_empty
								current_row[col] = ''
							col = col - 1
					break
			tree_list.append(new_row)

		tree_list.reverse()

		tree_string = ''

		if len(tree_list) > 0:
			first_line = tree_list.pop(0)
			tree_string += str(Path(*first_line)) + self.newline
			root_depth = len(first_line) - 1
			tree_list = list(map(lambda each: each[root_depth:], tree_list))

			for each in tree_list:
				tree_string += self.space.join(map(lambda x: str(x), [''] + each)) + self.newline

		self._filetree = tree_string


def main():
	""" Main routine """
	unittest.main()
	return 0


if __name__ == '__main__':
	import sys
	return_code = main()
	sys.exit(return_code)

