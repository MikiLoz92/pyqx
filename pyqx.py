#!/usr/bin/env python3:
#coding: utf-8

import sys, os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from mainwindow import MainWindow
from signals import Signals
from context import Context


def readCSS(fname):

	f = open(fname, 'r')
	s = f.read()
	f.close()

	return s


if __name__ == '__main__':

	app = QtWidgets.QApplication(sys.argv)
	#app.setWindowIcon(QtWidgets.QIcon("images/icon.png"))

	sys.setrecursionlimit(4096*4096)

	customFnt = "Lato-Reg.ttf"
	if QtGui.QFontDatabase().addApplicationFont(os.path.join("fonts", customFnt)) < 0:
		print("Warning: Could not load custom font" + customFnt + ", falling back to default font.")
	else:
		fnt = QtGui.QFont("Lato", 10)
		app.setFont(fnt)

	signals = Signals()
	context = Context(signals)

	mw = MainWindow(context, signals)
	mw.setStyleSheet(readCSS(os.path.join("themes", "algae", "style.css")))

	sys.exit(app.exec_())
