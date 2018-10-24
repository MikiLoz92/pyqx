#!/usr/bin/env python
#coding: utf-8

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

import names as Pixeler


class SizeLabel (QtWidgets.QLabel):

	def setValue(self, value):

		self.setText(str(value))


class ToolProperties (QtWidgets.QDockWidget):

	def __init__(self, title, context, signals, Parent=None):

		super(ToolProperties, self).__init__(title, Parent)

		self.context = context
		self.signals = signals
		self.parent = Parent
		self.setAllowedAreas(Qt.RightDockWidgetArea)
		self.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)

		# Llista de widgets (configuració de cada eina del programa)
		self.widgets = self.createWidgets()
		self.signals.updateTool.connect(self.updateWidget)

		self.updateWidget()

	def createWidgets(self):

		# Creem una llista amb tots el widgets i la retornem
		l = []

		l.append(self.createSelectionWidget())
		l.append(QtWidgets.QWidget())
		l.append(self.createPencilWidget())
		l.append(self.createEraserWidget())
		l.append(QtWidgets.QWidget())
		l.append(QtWidgets.QWidget())
		l.append(self.createGradientWidget())
		l.append(QtWidgets.QWidget())

		return l

	def createSelectionWidget(self):

		w = QtWidgets.QWidget()
		w.setObjectName("ToolProperties")
		w.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
		vbox = QtWidgets.QVBoxLayout()

		transparent = QtWidgets.QCheckBox(self.context.getText("tool_properties_selection", "transparent"), self)
		transparent.setChecked(self.context.transparentSelection)
		transparent.toggled.connect(self.context.setTransparentSelection)

		vbox.setAlignment(QtCore.Qt.AlignTop)
		vbox.addWidget(transparent)
		w.setLayout(vbox)

		return w

	def createPencilWidget(self):

		w = QtWidgets.QWidget()
		w.setObjectName("ToolProperties")
		w.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
		vbox = QtWidgets.QVBoxLayout()

		hbox1 = QtWidgets.QHBoxLayout()

		pencilSizeLabel = QtWidgets.QLabel(self.context.getText("tool_properties_pencil", "size"))
		slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
		slider.setValue(self.context.pencilSize)
		self.pencilSize = SizeLabel(str(self.context.pencilSize))

		slider.setMaximum(9)
		slider.setMinimum(1)
		slider.setPageStep(1)
		slider.setValue(self.context.pencilSize)
		slider.valueChanged.connect(self.context.setPencilSize)
		slider.valueChanged.connect(self.pencilSize.setValue)
		self.signals.updatePencilSize.connect(slider.setValue)

		hbox1.addWidget(pencilSizeLabel)
		hbox1.addWidget(slider)
		hbox1.addWidget(self.pencilSize)

		"""
		hbox2 = QtWidgets.QHBoxLayout()
		hbox2.addWidget(QtWidgets.QLabel("Alpha:"))
		alpha = QtWidgets.QSpinBox()
		alpha.setMinimum(0)
		alpha.setMaximum(255)
		alpha.setValue(255)
		alpha.valueChanged.connect(self.setPencilAlpha)
		alpha.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
		hbox2.addWidget(alpha)
		"""
		hbox2 = QtWidgets.QHBoxLayout()
		eraser = QtWidgets.QCheckBox(self.context.getText("tool_properties_pencil", "eraser"), self)
		eraser.setChecked(self.context.secondaryColorEraser)
		eraser.toggled.connect(self.toggleSecondaryColorEraser)
		hbox2.addWidget(eraser)

		vbox.setAlignment(QtCore.Qt.AlignTop)

		vbox.addLayout(hbox1)
		vbox.addLayout(hbox2)
		w.setLayout(vbox)

		return w

	def setPencilSize(self, size):

		self.pencilSize.setText(str(size))
		self.context.pencilSize = size

	def setPencilAlpha(self, alpha):

		self.context.pencilAlpha = alpha

	def toggleSecondaryColorEraser(self):

		self.context.secondaryColorEraser = not self.context.secondaryColorEraser

	def createEraserWidget(self):

		w = QtWidgets.QWidget()
		w.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
		vbox = QtWidgets.QVBoxLayout()

		hbox = QtWidgets.QHBoxLayout()

		eraserSizeLabel = QtWidgets.QLabel(self.context.getText("tool_properties_eraser", "size"))
		slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
		slider.setValue(self.context.eraserSize)
		self.eraserSize = SizeLabel(str(self.context.eraserSize))

		slider.setMaximum(9)
		slider.setMinimum(1)
		slider.setPageStep(1)
		slider.setValue(self.context.eraserSize)
		slider.valueChanged.connect(self.context.setEraserSize)
		slider.valueChanged.connect(self.eraserSize.setValue)
		self.signals.updateEraserSize.connect(slider.setValue)

		hbox.addWidget(eraserSizeLabel)
		hbox.addWidget(slider)
		hbox.addWidget(self.eraserSize)

		vbox.setAlignment(QtCore.Qt.AlignTop)

		vbox.addLayout(hbox)
		w.setLayout(vbox)

		return w

	def setEraserSize(self, size):

		self.eraserSize.setText(str(size))
		self.context.eraserSize = size

	def createGradientWidget(self):

		self.v = QtWidgets.QVBoxLayout()

		v2 = QtWidgets.QVBoxLayout()

		self.btn1 = QtWidgets.QRadioButton(self.context.getText("tool_properties_gradient", "horizontal"))
		self.btn2 = QtWidgets.QRadioButton(self.context.getText("tool_properties_gradient", "vertical"))
		self.btn1.setChecked(True)

		self.btn1.clicked.connect( lambda : self.changeDegDir('H') )
		self.btn2.clicked.connect( lambda : self.changeDegDir('V') )

		h = QtWidgets.QHBoxLayout()

		self.label = QtWidgets.QLabel("Transparencia:", self)

		self.AlphaSpin = QtWidgets.QSpinBox(self) 
		self.AlphaSpin.setMinimum(0)
		self.AlphaSpin.setMaximum(255)
		self.AlphaSpin.setValue(255)
		self.AlphaSpin.valueChanged.connect(self.setAlphaValue)

		h.addWidget(self.label)
		h.addWidget(self.AlphaSpin)
		tmp = QtWidgets.QWidget()
		tmp.setLayout(h) 

		self.check = QtWidgets.QCheckBox("Color a Transparente")
		self.check.stateChanged.connect(self.changeDegState)

		v2.addWidget(self.btn1)
		v2.addWidget(self.btn2)
		tmp2 = QtWidgets.QWidget()
		tmp2.setLayout(v2) 

		self.v.addWidget(tmp2) 
		#self.v.addWidget(tmp)
		#self.v.addWidget(self.check)

		w = QtWidgets.QWidget()
		w.setLayout(self.v)
		self.v.addStretch()

		return w


	def changeDegDir(self, state):
		if self.btn1.isChecked():
			self.context.DegDir = 'H'
		elif self.btn2.isChecked():
			self.context.DegDir = 'V'

	def changeDegState(self):
		if self.check.isChecked():
			self.context.DegState = 1
		else:
			self.context.DegState = 2

	def setAlphaValue(self):
		self.context.DegAlpha = self.AlphaSpin.value()
		print(self.context.DegAlpha)

	def updateWidget(self):
		self.setWidget(self.widgets[self.context.currentTool])
