#!/usr/bin/env python
#coding: utf-8

import os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

## Vista/View
class NewFileDialog(QtWidgets.QDialog):
	"""
	La ventanita que se abre cuando queremos crear un archivo nuevo.
	"""

	def __init__(self, context, Parent=None):

		super(NewFileDialog,self).__init__(Parent)
		self.context = context
		self.parent = Parent

		dimensionGroup = QtWidgets.QGroupBox(self.context.getText("dialog_new_image", "dimension"))
		dimensionLayout = QtWidgets.QVBoxLayout()

		self.width = QtWidgets.QSpinBox(dimensionGroup)
		self.width.setMinimum(1)
		self.width.setMaximum(4096)
		self.width.setValue(self.context.getIntDefault("new", "width", 32))
		self.height = QtWidgets.QSpinBox(dimensionGroup)
		self.height.setMinimum(1)
		self.height.setMaximum(4096)
		self.height.setValue(self.context.getIntDefault("new", "height", 32))

		clipboard = QtWidgets.QApplication.clipboard()
		print("Accesses clipboard")
		im = clipboard.image()
		if not im.isNull():
			print("Image not null")
			self.width.setValue(im.width())
			self.height.setValue(im.height())
		
		dimensionLayout.addWidget(self.width)
		dimensionLayout.addWidget(self.height)
		dimensionGroup.setLayout(dimensionLayout)

		backgroundGroup = QtWidgets.QGroupBox(self.context.getText("dialog_new_image", "background"))
		backgroundLayout = QtWidgets.QVBoxLayout()
		self.r1 = QtWidgets.QRadioButton(self.context.getText("dialog_new_image", "transparent"))
		self.r1.setChecked(True)
		self.r2 = QtWidgets.QRadioButton(self.context.getText("dialog_new_image", "color"))
		self.cButton = QtWidgets.QPushButton()
		self.cButton.clicked.connect(self.getColor)
		self.cButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
		self.color = QtGui.QColor(255,255,255)
		self.cButton.setStyleSheet("background-color: " + self.color.name() +";")
		self.cButton.setText(self.color.name())
		colorLayout = QtWidgets.QHBoxLayout()
		colorLayout.addWidget(self.r2)
		colorLayout.addWidget(self.cButton)
		backgroundLayout.addWidget(self.r1)
		#backgroundLayout.addWidget(r2)
		backgroundLayout.addLayout(colorLayout)
		backgroundGroup.setLayout(backgroundLayout)

		buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
		#buttonBox.accepted.connect(self.accept)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)
		mainLayout = QtWidgets.QVBoxLayout()
		mainLayout.addWidget(dimensionGroup)
		mainLayout.addWidget(backgroundGroup)
		mainLayout.addWidget(buttonBox)
		self.setLayout(mainLayout)
		self.setWindowTitle(self.context.getText("dialog_new_image", "title"))
		self.initUI()

	def initUI(self):

		self.show()

	def getColor(self):

		self.color = QtWidgets.QColorDialog.getColor()
		if self.color.isValid(): 
			self.r2.setChecked(True)
			self.cButton.setStyleSheet("background-color: " + self.color.name() +";")
			self.cButton.setText(self.color.name())

	def accept(self):

		if self.r1.isChecked():
			self.context.newImage(self.width.value(), self.height.value(), QtGui.QColor(0,0,0,0))
		else:
			self.context.newImage(self.width.value(), self.height.value(), self.color)
		self.context.setDefault("new", "width", str(self.width.value()))
		self.context.setDefault("new", "height", str(self.height.value()))
		super(NewFileDialog, self).accept()


class ResizeImageDialog (QtWidgets.QDialog):

	def __init__(self, context, Parent=None):

		super(ResizeImageDialog, self).__init__(Parent)

		self.context = context
		self.parent = Parent

		dimensionGroup = QtWidgets.QGroupBox(self.context.getText("dialog_resize", "dimension"))
		dimensionLayout = QtWidgets.QVBoxLayout()

		self.width = QtWidgets.QSpinBox(dimensionGroup)
		self.width.setMinimum(1)
		self.width.setMaximum(4096)
		self.width.setValue(self.context.currentQImage().width())
		self.height = QtWidgets.QSpinBox(dimensionGroup)
		self.height.setMinimum(1)
		self.height.setMaximum(4096)
		self.height.setValue(self.context.currentQImage().height())

		dimensionLayout.addWidget(self.width)
		dimensionLayout.addWidget(self.height)
		dimensionGroup.setLayout(dimensionLayout)
		
		buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		mainLayout = QtWidgets.QVBoxLayout()
		mainLayout.addWidget(dimensionGroup)
		mainLayout.addWidget(buttonBox)

		self.setLayout(mainLayout)
		self.setWindowTitle(self.context.getText("dialog_resize", "title"))
		self.show()

	def accept(self):
	
		self.context.resizeImage(self.width.value(), self.height.value())
		super(ResizeImageDialog,self).accept()


class ResizeCanvasDialog (QtWidgets.QDialog):

	def __init__(self, context, Parent=None):

		super(ResizeCanvasDialog, self).__init__(Parent)

		self.context = context
		self.parent = Parent

		dimensionGroup = QtWidgets.QGroupBox(self.context.getText("dialog_resize_canvas", "dimension"))
		dimensionLayout = QtWidgets.QVBoxLayout()

		self.width = QtWidgets.QSpinBox(dimensionGroup)
		self.width.setMinimum(1)
		self.width.setMaximum(1024)
		self.width.setValue(self.context.currentQImage().width())
		self.height = QtWidgets.QSpinBox(dimensionGroup)
		self.height.setMinimum(1)
		self.height.setMaximum(1024)
		self.height.setValue(self.context.currentQImage().height())

		dimensionLayout.addWidget(self.width)
		dimensionLayout.addWidget(self.height)
		dimensionGroup.setLayout(dimensionLayout)
		
		buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		mainLayout = QtWidgets.QVBoxLayout()
		mainLayout.addWidget(dimensionGroup)
		mainLayout.addWidget(buttonBox)

		self.setLayout(mainLayout)
		self.setWindowTitle(self.context.getText("dialog_resize_canvas", "title"))
		self.show()

	def accept(self):
	
		self.context.resizeCanvas(self.width.value(), self.height.value())
		super(ResizeCanvasDialog,self).accept()


class Preferences (QtWidgets.QDialog):

	def  __init__(self, context, signals, Parent=None):

		super(Preferences, self).__init__(Parent)
		self.context = context
		self.signals = signals
		self.parent = Parent

		# El QStackedWidget es un tipo de widget muy útil que tiene diferentes "páginas" y podemos ir cambiando entre ellas
		# con sólo llamar a un método. En nuestro caso, conectamos el signal que emite el QListWidget al cambiar de sección
		# con el método self.changeCurrentView, que cambia la página del QStackedWidget.

		self.view = QtWidgets.QStackedWidget()
		self.view.addWidget(self.createLanguageView())
		self.view.addWidget(self.createUICustomizationView())
		self.view.addWidget(self.createMatrixGridView())

		self.preferences = QtWidgets.QListWidget()
		self.preferences.addItem(self.context.getText("dialog_preferences", "item_language"))
		self.preferences.addItem(self.context.getText("dialog_preferences", "item_theme"))
		self.preferences.addItem(self.context.getText("dialog_preferences", "item_matrix_grid"))
		self.preferences.setCurrentRow(0)
		self.preferences.currentItemChanged.connect(self.changeCurrentView)
		self.preferences.setFixedWidth(self.preferences.sizeHintForColumn(0) + 24)
		#self.view.setFixedWidth(200)

		self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)

		self.hbox = QtWidgets.QHBoxLayout()
		self.hbox.addWidget(self.preferences)
		self.hbox.addWidget(self.view)

		self.vbox = QtWidgets.QVBoxLayout()
		self.vbox.addLayout(self.hbox)
		self.vbox.addWidget(self.buttonBox)

		self.setLayout(self.vbox)
		self.setWindowTitle(self.context.getText("dialog_preferences", "title"))
		self.adjustSize()
		self.show()

	def changeCurrentView(self):

		self.view.setCurrentIndex(self.preferences.currentRow())

	def createLanguageView(self):

		# Widget de ejemplo

		g = QtWidgets.QGroupBox(self.context.getText("dialog_preferences", "item_language_language"))

		w = QtWidgets.QWidget()

		vbox = QtWidgets.QVBoxLayout()

		self.language = QtWidgets.QComboBox()
		self.langCodes = []

		j = 0
		for i in self.context.tdatabase.d.keys():
			self.language.addItem(self.context.tdatabase.d[i].name)
			langCode = self.context.tdatabase.d[i].code
			self.langCodes.append(langCode)
			if self.context.lang == langCode:
				self.language.setCurrentIndex(j)
			j += 1

		vbox.addWidget(self.language)
		vbox.setStretch(1,1)
		vbox.setAlignment(Qt.AlignTop)

		w.setLayout(vbox)

		g.setLayout(vbox)

		return g

	def createUICustomizationView(self):

		g = QtWidgets.QGroupBox(self.context.getText("dialog_preferences", "item_theme"))
		w = QtWidgets.QWidget()
		vbox = QtWidgets.QVBoxLayout()
		hbox = QtWidgets.QHBoxLayout()

		self.theme = QtWidgets.QComboBox()

		j = 0
		self.themeDirs = [d for d in os.listdir("themes") if os.path.isdir(os.path.join("themes", d))]
		for i in self.themeDirs:
			self.theme.addItem(i)
			if self.context.theme == i:
				self.theme.setCurrentIndex(j)
			j += 1
		self.theme.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
		#self.theme.setFixedWidth(self.theme.sizeHint().width())

		hbox.addWidget(QtWidgets.QLabel(self.context.getText("dialog_preferences", "item_theme_theme")))
		hbox.addWidget(self.theme)
		hbox.setAlignment(Qt.AlignLeft)
		vbox.addLayout(hbox)

		vbox.setStretch(1,1)
		vbox.setAlignment(Qt.AlignTop)

		w.setLayout(vbox)
		g.setLayout(vbox)

		return g

	def createMatrixGridView(self):

		g = QtWidgets.QGroupBox(self.context.getText("dialog_preferences", "item_matrix_grid_dimension"))

		vbox = QtWidgets.QVBoxLayout()
		
		self.matrixGridWidth = QtWidgets.QSpinBox()
		self.matrixGridWidth.setMinimum(1)
		self.matrixGridWidth.setMaximum(1024)
		self.matrixGridWidth.setValue(self.context.matrixGridWidth)
		self.matrixGridHeight = QtWidgets.QSpinBox()
		self.matrixGridHeight.setMinimum(1)
		self.matrixGridHeight.setMaximum(1024)
		self.matrixGridHeight.setValue(self.context.matrixGridHeight)

		vbox.addWidget(self.matrixGridWidth)
		vbox.addWidget(self.matrixGridHeight)
		vbox.setStretch(1,1)
		vbox.setAlignment(Qt.AlignTop)

		g.setLayout(vbox)

		return g

	def accept(self):

		if self.langCodes[self.language.currentIndex()] != self.context.lang:
			QtWidgets.QMessageBox.information(self, self.context.getText("dialog_preferences", "item_language_changed_title"), self.context.getText("dialog_preferences", "item_language_changed_message"))
		self.context.setDefault("language", "lang", self.langCodes[self.language.currentIndex()])

		self.context.matrixGridWidth = self.matrixGridWidth.value()
		self.context.setDefault("grid", "matrix_grid_width", self.context.matrixGridWidth)
		self.context.matrixGridHeight = self.matrixGridHeight.value()
		self.context.setDefault("grid", "matrix_grid_height", self.context.matrixGridHeight)

		if self.context.getDefault("theme", "theme", "aquamarine") != self.themeDirs[self.theme.currentIndex()]:
			QtWidgets.QMessageBox.information(self, self.context.getText("dialog_preferences", "item_theme_changed_title"), self.context.getText("dialog_preferences", "item_theme_changed_message"))
		self.context.setDefault("theme", "theme", self.themeDirs[self.theme.currentIndex()])

		self.signals.updateCanvas.emit()
		super(Preferences, self).accept()
