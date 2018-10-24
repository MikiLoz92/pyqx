#!/usr/bin/env python
#coding: utf-8

from PyQt5 import QtCore

class Signals(QtCore.QObject):
	"""
	La clase Communication hace de puente entre diferentes
	instancias de todo el programa.
	"""

	newImage = QtCore.pyqtSignal()
	imageChanged = QtCore.pyqtSignal([int])
	imageRemoved = QtCore.pyqtSignal([int])
	fileNameChanged = QtCore.pyqtSignal([int, str])

	updateCanvas = QtCore.pyqtSignal()
	resizeCanvas = QtCore.pyqtSignal()

	copyImage = QtCore.pyqtSignal()
	cutImage = QtCore.pyqtSignal()
	pasteImage = QtCore.pyqtSignal()
	clearImage  = QtCore.pyqtSignal()

	updateColor = QtCore.pyqtSignal()
	updateColorDeg = QtCore.pyqtSignal()

	ctrlPressed = QtCore.pyqtSignal()

	updateTool = QtCore.pyqtSignal([int])
	autoUpdateTool = QtCore.pyqtSignal([int])

	transparentSelection = QtCore.pyqtSignal([bool])

	zoom = QtCore.pyqtSignal()

	colorPickerOn = QtCore.pyqtSignal()
	colorPickerOff = QtCore.pyqtSignal()

	enterCanvas = QtCore.pyqtSignal()
	leaveCanvas = QtCore.pyqtSignal()
	overCanvas = QtCore.pyqtSignal([int, int])

	updatePencilSize = QtCore.pyqtSignal([int])
	updateEraserSize = QtCore.pyqtSignal([int])
