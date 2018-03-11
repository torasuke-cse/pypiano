#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module provides some tools such as shell-commands on UNIX systems.

This module includes unit test suite for itself.
Please execute following command on your shell.

$ python shell.py

If you need more information for test result, execute it with '--verbose'.
"""

__author__    = 'MIYAZAKI Masafumi (The Project Fukurous)'
__date__      = '2017/03/20'
__version__   = '0.0.9'

__copyright__ = "Copyright 2017 MIYAZAKI Masafumi (The Project Fukurous)"
__license__   = 'The 2-Clause BSD License'


import codecs
import os
import re
import sys
import tempfile
import unittest


class TestMyshell(unittest.TestCase):
	""" Test suite for MyShell """

	def test_case_01(self):
		""" Test case for set_list, get_list """
		a_list = ['a', 'b', 'c']
		another_list = []

		instance = MyShell()

		instance.set_list(a_list)
		instance.get_list(another_list)

		self.assertEqual(another_list[0], 'a')
		self.assertEqual(another_list[1], 'b')
		self.assertEqual(another_list[2], 'c')

	def test_case_02(self):
		""" Test case for append_list """
		first_list = ['a', 'b']
		second_list = ['c', 'd']
		result_list = []

		instance = MyShell()

		instance.set_list(first_list)
		instance.append_list(second_list)
		instance.get_list(result_list)

		self.assertEqual(result_list, ['a', 'b', 'c', 'd'])

	def test_case_03(self):
		""" Test case for clear """
		a_list = ['a', 'b', 'c']
		another_list = []

		instance = MyShell()

		instance.set_list(a_list)
		instance.clear()
		instance.get_list(another_list)

		self.assertEqual(another_list, [])

	def test_case_04(self):
		""" Test case for append_element """
		a_list = ['a', 'b', 'c']
		another_list = []

		instance = MyShell()

		instance.set_list(a_list)
		instance.append_element('d')
		instance.get_list(another_list)

		self.assertEqual(another_list, ['a', 'b', 'c', 'd'])

	def test_case_05(self):
		""" Test case for clone """
		a_list = ['a', 'b', 'c']
		first_list = []
		second_list = []

		first_instance = MyShell()
		first_instance.set_list(a_list)
		first_instance.get_list(first_list)

		second_instance = first_instance.clone()
		second_instance.get_list(second_list)

		self.assertTrue(first_list == second_list)
		self.assertFalse(first_list is second_list)

		second_instance.append_element('d')
		second_instance.get_list(second_list)

		self.assertFalse(first_list == second_list)

	def test_case_06(self):
		""" Test case for yourself """
		instance = MyShell()

		self.assertEqual(instance, instance.yourself())

	def test_case_07(self):
		""" Test case for sort, rsort, reverse """
		a_list = ['1', 'a', '2', 'b', '10']
		first_list = []
		second_list = []

		first_instance = MyShell()
		first_instance.set_list(a_list)
		second_instance = first_instance.clone()

		first_instance.sort()
		first_instance.get_list(first_list)

		self.assertEqual(first_list, ['1', '10', '2', 'a', 'b'])

		second_instance.rsort()
		second_instance.get_list(second_list)

		self.assertEqual(second_list, ['b', 'a', '2', '10', '1'])

		second_instance.reverse()
		second_instance.get_list(second_list)

		self.assertEqual(first_list, second_list)

	def test_case_08(self):
		""" Test case for map """
		a_list = ['a', 'c', 'b']
		another_list = []

		instance = MyShell()

		instance.set_list(a_list)
		instance.map(lambda x: x.upper())
		instance.get_list(another_list)

		self.assertEqual(another_list, ['A', 'C', 'B'])

	def test_case_09(self):
		""" Test case for grep, ungrep """
		a_list = ['cat', 'cut', 'cup', 'map']
		another_list = []

		first_instance = MyShell()
		first_instance.set_list(a_list)

		second_instance = first_instance.clone()

		first_instance.grep(re.compile('.a.'))
		first_instance.get_list(another_list)

		self.assertEqual(another_list, ['cat', 'map'])

		second_instance.ungrep(re.compile('.a.'))
		second_instance.get_list(another_list)

		self.assertEqual(another_list, ['cut', 'cup'])

	def test_case_10(self):
		""" Test case for replace """
		a_list = ['a1b2c', '3d4e5']
		another_list = []

		instance = MyShell()

		instance.set_list(a_list)
		instance.replace(re.compile('[0-9]'), '-')
		instance.get_list(another_list)

		self.assertEqual(another_list, ['a-b-c', '-d-e-'])

	def test_case_11(self):
		""" Test case for strip, rstrip, lstrip """
		a_list = ['  both sides  ', 'right side  ', '  left side']
		another_list = []

		first_instance = MyShell()
		first_instance.set_list(a_list)

		second_instance = first_instance.clone()
		third_instance = first_instance.clone()

		first_instance.strip()
		first_instance.get_list(another_list)

		self.assertEqual(another_list, ['both sides', 'right side', 'left side'])

		second_instance.rstrip()
		second_instance.get_list(another_list)

		self.assertEqual(another_list, ['  both sides', 'right side', '  left side'])

		third_instance.lstrip()
		third_instance.get_list(another_list)

		self.assertEqual(another_list, ['both sides  ', 'right side  ', 'left side'])

	def test_case_12(self):
		""" Test case for unique """
		a_list = ['a', 'b', 'c', 'c', 'a']
		another_list = []

		instance = MyShell()

		instance.set_list(a_list)
		instance.unique()
		instance.get_list(another_list)

		self.assertEqual(another_list, ['a', 'b', 'c'])

	def test_case_13(self):
		""" Test case for list """
		a_list = ['a', 'b', 'c']

		instance = MyShell()

		instance.set_list(a_list)

		self.assertEqual(instance.list, ['a', 'b', 'c'])

	def test_case_14(self):
		""" Test case for union, union_all """
		a_list = ['a', 'b', 'c']
		another_list = ['a', 'c', 'e']

		first_instance = MyShell()
		first_instance.set_list(a_list)

		second_instance = first_instance.clone();

		third_instance = MyShell()
		third_instance.set_list(another_list)

		first_instance.union_all(third_instance)

		self.assertEqual(first_instance.list, ['a', 'b', 'c', 'a', 'c', 'e'])

		second_instance.union(third_instance)

		self.assertEqual(second_instance.list, ['a', 'b', 'c', 'e'])

	def test_case_15(self):
		""" Test case for extension of constructor """
		a_list = ['a', 'b', 'c']

		first_instance = MyShell()

		self.assertEqual(first_instance.list, [])

		second_instance = MyShell(a_list)

		self.assertEqual(second_instance.list, ['a', 'b', 'c'])

	def test_case_16(self):
		""" Test case for intersect """
		first_list = ['a', 'c', 'e', 'g']
		second_list = ['b', 'c', 'd', 'e', 'f']

		first_instance = MyShell(first_list)
		second_instance = MyShell(second_list)

		first_instance.intersect(second_instance)

		self.assertEqual(first_instance.list, ['c', 'e'])

	def test_case_17(self):
		""" Test case for size """
		a_list = ['a', 'b', 'c']

		instance = MyShell()

		self.assertEqual(instance.size(), 0)

		instance.set_list(a_list)

		self.assertEqual(instance.size(), 3)

	def test_case_18(self):
		""" Test case for shuffle (Actually, it's not testable...) """
		a_list = list(map(lambda x: str(x), range(100)))
		saved_list = a_list.copy()

		instance = MyShell(a_list)
		instance.shuffle()

		# print()
		# print('A : {0}'.format(','.join(instance.list())))
		# print('B : {0}'.format(','.join(saved_list)))

		self.assertNotEqual(instance.list, saved_list)

	def test_case_19(self):
		""" Test case for newline, encoding """
		instance = MyShell()

		self.assertEqual(instance.newline, os.linesep)
		self.assertEqual(instance.encoding, sys.getdefaultencoding())

		instance.newline = '\r\n'
		instance.encoding = 'shift_jis'

		self.assertEqual(instance.newline, '\r\n')
		self.assertEqual(instance.encoding, 'shift_jis')

	def test_case_20(self):
		""" Test case for write_to_file, append_to_file, read_from_file, append_from_file """
		the_file = tempfile.NamedTemporaryFile('w', delete = False)
		the_file.close()
		# print(the_file.name)

		try:
			first_instance = MyShell(['a', 'b', ''])
			first_instance.write_to_file(the_file.name)

			second_instance = MyShell(['c', 'd'])
			second_instance.append_to_file(the_file.name)

			third_instance = MyShell()
			third_instance.read_from_file(the_file.name)

			self.assertEqual(third_instance.list, ['a', 'b', '', 'c', 'd'])

			third_instance.append_from_file(the_file.name)

			self.assertEqual(third_instance.list, ['a', 'b', '', 'c', 'd', 'a', 'b', '', 'c', 'd'])

		finally:
			os.remove(the_file.name)

	def test_case_21(self):
		""" Test case for minus, minus_all """
		a_list = ['a', 'a', 'b', 'c']
		another_list = ['a', 'c', 'e']

		first_instance = MyShell(a_list)
		second_instance = first_instance.clone()
		third_instance = MyShell(another_list)

		first_instance.minus(third_instance)

		self.assertEqual(first_instance.list, ['a', 'b'])

		second_instance.minus_all(third_instance)

		self.assertEqual(second_instance.list, ['b'])

	def test_case_22(self):
		""" Test case for foreach """
		a_list = ['a', 'b', 'c']
		another_list = []

		instance = MyShell(a_list)
		instance.foreach(lambda each: another_list.append(each.upper()))

		self.assertEqual(another_list, ['A', 'B', 'C'])

	def test_case_23(self):
		""" Test case for split """
		a_list = ['a-b+c', 'd@e']

		instance = MyShell(a_list)
		instance.split(re.compile('[-+@]'))

		self.assertEqual(instance.list, ['a', 'b', 'c', 'd', 'e'])

	def test_case_24(self):
		""" Test case for join """
		a_list = ['<', 'a', '>', 'b', '<', '>', '<', 'c', 'd', '>', '<', 'e', 'f']

		instance = MyShell(a_list)
		instance.join('-', re.compile('<'), re.compile('>'))

		self.assertEqual(instance.list, ['<-a->', 'b', '<->', '<-c-d->', '<-e-f'])

	def test_case_25(self):
		""" Test case for line_number """
		a_list = ['a', 'bc', '', 'def']

		instance = MyShell(a_list)
		instance.line_number()

		self.assertEqual(instance.list, ['1 : a', '2 : bc', '3 : ', '4 : def'])

	def test_case_26(self):
		""" Test case for __str__ """
		a_list = ['hoge', 'foo', '', 'bar']

		instance = MyShell(a_list)
		instance.newline = '\n'

		self.assertEqual(str(instance), 'hoge\nfoo\n\nbar')

	def test_case_27(self):
		""" Test case for __repr__ """
		a_list = ['ho\nge', 'foo', '', 'bar']

		instance = MyShell(a_list)

		self.assertEqual(repr(instance), r"MyShell(['ho\nge','foo','','bar'])")


class MyShell(object):
	""" I provide some tools such as shell-commands on UNIX systems. """

	### Basic Functions ###

	def __init__(self, the_list = None):
		""" I born now and have a list. It's myself. """
		if the_list is None:
			self._list = []
		else:
			self._list = the_list

		self._newline = self._default_newline()
		self._encoding = self._default_encoding()

	def __str__(self):
		""" I introduce myself. """
		return self.newline.join(self._list)

	def __repr__(self):
		""" I represent myself strictly. """
		a_list = []
		self.foreach(lambda each: a_list.append(repr(each)))
		return 'MyShell([{0}])'.format(','.join(a_list))

	def clone(self):
		""" I copy myself. """
		my_clone = MyShell()
		my_clone.set_list(self._list.copy())
		return my_clone

	### Chained Functions ###

	def foreach(self, the_lambda):
		""" I do the_lambda to each element in myself. """
		for each in self._list:
			the_lambda(each)
		return self

	def map(self, the_lambda):
		""" I apply the_lambda to each element in myself. """
		self._list = list(map(the_lambda, self._list))
		return self

	def sort(self):
		""" I sort myself in ascending order. """
		self._list.sort(reverse = False)
		return self

	def rsort(self):
		""" I sort myself in descending order. """
		self._list.sort(reverse = True)
		return self

	def reverse(self):
		""" I reverse myself. """
		self._list.reverse()
		return self

	def write_to_file(self, the_filename):
		""" I write data to the_filename. """
		with open(the_filename, 'w', encoding = self.encoding) as the_file:
			the_file.write(self.newline.join(self._list + ['']))
		return self

	def append_to_file(self, the_filename):
		""" I append data to the_filename. """
		with open(the_filename, 'a', encoding = self.encoding) as the_file:
			the_file.write(self.newline.join(self._list + ['']))
		return self

	def read_from_file(self, the_filename):
		""" I read data from the_filename and set it as new myself. """
		self.clear()
		self.append_from_file(the_filename)
		return self

	def append_from_file(self, the_filename):
		""" I append data from the_filename to myself. """
		with open(the_filename, 'r', encoding = self.encoding, newline = self.newline) as the_file:
			lines = the_file.read()
			self.append_list(lines.splitlines())
		return self

	def append_list(self, the_list):
		""" I append the_list to myself. """
		self._list.extend(the_list)
		return self

	def append_element(self, the_element):
		""" I append the_element to myself. """
		self._list.append(the_element)
		return self

	def unique(self):
		""" I forget elements that they are duplicated. """
		new_list = []

		for each in self._list:
			if each not in new_list:
				new_list.append(each)

		self._list = new_list

		return self

	def clear(self):
		""" I forget myself. """
		self._list = []
		return self

	def line_number(self, the_padding = ' '):
		""" I add the line number for each line. """
		digits = len(str(self.size()))
		adjusted_number = (lambda x: str(x).rjust(digits, the_padding))

		for index in range(self.size()):
			self._list[index] = '{0} : {1}'.format(adjusted_number(index + 1), self._list[index])

		return self

	def set_list(self, the_list):
		""" I set the_list to me. """
		self._list = the_list
		return self

	def get_list(self, the_list):
		""" I give myself to the_list. """
		the_list.clear()
		the_list.extend(self._list)
		return self

	def union(self, the_shell):
		""" I unite elements that they are not included in myself. """
		the_list = []

		the_shell.get_list(the_list)

		for each in the_list:
			if each not in self._list:
				self.append_element(each)

		return self

	def union_all(self, the_shell):
		""" I unite with the_shell. """
		the_list = []
		the_shell.get_list(the_list)

		self.append_list(the_list)

		return self

	def minus(self, the_shell):
		""" I reduce elements that they are included in the_shell. """
		new_list = []
		the_list = []

		the_shell.get_list(the_list)

		for each in the_list:
			if each in self._list:
				self._list.remove(each)

		return self

	def minus_all(self, the_shell):
		""" I reduce elements that they are included in the_shell. """
		new_list = []
		the_list = []

		the_shell.get_list(the_list)

		for each in self._list:
			if each not in the_list:
				new_list.append(each)

		self._list = new_list

		return self

	def intersect(self, the_shell):
		""" I do multiplication with the_shell. """
		new_list = []
		the_list = []

		the_shell.get_list(the_list)

		for each in self._list:
			if each in the_list:
				new_list.append(each)

		self._list = new_list

		return self

	def split(self, the_regex):
		""" I split each element with the_regex. """
		new_list = []

		self.foreach(lambda each: new_list.extend(the_regex.split(each)))

		self._list = new_list

		return self

	def join(self, the_glue, start_regex, end_regex):
		""" I join elements with the_glue. """
		new_list = []
		temporary_list = []

		for each in self._list:
			if temporary_list == []:
				if start_regex.search(each) == None:
					new_list.append(each)
				else:
					temporary_list.append(each)
			else:
				temporary_list.append(each)
				if end_regex.search(each) != None:
					new_list.append(the_glue.join(temporary_list))
					temporary_list = []

		if temporary_list != []:
			new_list.append(the_glue.join(temporary_list))

		self._list = new_list

		return self

	def yourself(self):
		""" I'm just me. """
		return self

	def replace(self, the_regex, string):
		""" I update myself with the_regex for replacement. """
		self.map(lambda each: the_regex.sub(string, each))
		return self

	def grep(self, the_regex):
		""" I forget elements that they do not match the_regex. """
		new_list = []

		for each in self._list:
			if the_regex.search(each) != None:
				new_list.append(each)

		self._list = new_list

		return self

	def ungrep(self, the_regex):
		""" I forget elements that they match the_regex. """
		new_list = []

		for each in self._list:
			if the_regex.search(each) == None:
				new_list.append(each)

		self._list = new_list

		return self

	def strip(self):
		""" I strip myself from both sides. """
		self.map(lambda each: each.strip())
		return self

	def rstrip(self):
		""" I strip myself from right side. """
		self.map(lambda each: each.rstrip())
		return self

	def lstrip(self):
		""" I strip myself from left side. """
		self.map(lambda each: each.lstrip())
		return self

	def shuffle(self):
		""" I shuffle myself. """
		import random
		random.shuffle(self._list)
		return self

	def print(self):
		""" I show all elements in myself. """
		self.foreach(lambda each: print(each))
		return self

	def print_with_line(self):
		""" I show all elements in myself with 1 line. """
		print(','.join(self._list))
		return self

	### Non-Chained Functions ###

	def size(self):
		""" I tell you the size of myself. """
		my_size = len(self._list)
		return my_size

	@property
	def list(self):
		""" I tell you myself. It's ashamed... """
		myself = self._list
		return myself

	@property
	def newline(self):
		""" I tell you my newline character. """
		return self._newline

	@newline.setter
	def newline(self, the_string):
		""" I remember the_string as newline character. """
		self._newline = the_string
		return

	def _default_newline(self):
		""" I think this is default newline. """
		return os.linesep

	@property
	def encoding(self):
		""" I tell you my encoding. """
		return self._encoding

	@encoding.setter
	def encoding(self, the_string):
		""" I remember the_string as my encoding. """
		self._encoding = the_string
		return

	def _default_encoding(self):
		""" I think this is default encoding. """
		return sys.getdefaultencoding()


def main():
	""" Main routine """
	unittest.main()
	return 0


if __name__ == '__main__':
	import sys
	return_code = main()
	sys.exit(return_code)

