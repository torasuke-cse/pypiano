#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pypiano.pyを実行するだけのプログラムです。
"""

__author__ = 'AOKI Yuji'
__version__ = '1.0.0'
__date__ = '2018/05/06 (Created: 2018/05/06)'

# 組み込みモジュールsysをインポートする。exit関数を用いるために。
import sys

# org.fukurous.appsというパッケージの中のpypianoモジュールをpypianoとしてインポートする。
import org.fukurous.apps.pypiano as pypiano

if __name__ == '__main__':
	# 上記のifによって、このスクリプトファイルが直接実行されたときだけ、以下の部分を実行する。

	# pypianoモジュールのmain()を呼び出して結果を得て、Pythonシステムに終わりを告げる。
	sys.exit(pypiano.main())
