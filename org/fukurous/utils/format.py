#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for various formats.

This module includes unit test suite for itself.
Please execute following command on your shell.

$ python format.py

If you need more information for test result, execute it with '--verbose'.
"""

__author__    = 'MIYAZAKI Masafumi (The Project Fukurous)'
__date__      = '2017/03/20'
__version__   = '0.0.0'

__copyright__ = "Copyright 2017 MIYAZAKI Masafumi (The Project Fukurous)"
__license__   = 'The 2-Clause BSD License'


import unittest


class TestFormat(unittest.TestCase):
	""" Test suite for format """

	def test_case_01(self):
		""" Test case for ... """
		pass


def main():
	""" Main routine """
	unittest.main()
	return 0


if __name__ == '__main__':
	import sys
	return_code = main()
	sys.exit(return_code)

