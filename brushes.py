#!/usr/bin/env python
#coding: utf-8

from PyQt5 import QtWidgets, QtCore, QtGui


def createBrushes():

	circles = []
	brushes = []

	for i in range(9):
		m, im = createCircle(i)
		circles.append(m)
		pm = QtGui.QBitmap().fromImage(im)
		brushes.append(pm)

	return circles, brushes


def createCircle(radius):

		im = QtGui.QImage(QtCore.QSize(radius*2+1, radius*2+1), QtGui.QImage.Format_Mono)
		im.fill(QtCore.Qt.color1)
		x0 = radius
		y0 = radius
		f = 1 - radius
		ddf_x = 1
		ddf_y = -2 * radius
		x = 0
		y = radius
		l = []
		for i in range(2*radius+1):
			l.append([False]*(2*radius+1))
		l[y0+radius][x0] = True
		im.setPixel(x0, y0+radius, QtCore.Qt.color0)
		l[y0-radius][x0] = True
		im.setPixel(x0, y0-radius, QtCore.Qt.color0)
		l[y0][x0+radius] = True
		im.setPixel(x0+radius, y0, QtCore.Qt.color0)
		l[y0][x0-radius] = True
		im.setPixel(x0-radius, y0, QtCore.Qt.color0)
		while x < y:
			if f >= 0: 
				y -= 1
				ddf_y += 2
				f += ddf_y
			x += 1
			ddf_x += 2
			f += ddf_x
			for i in range(x0-x,x0+x+1):
				l[y0+y][i] = True
				im.setPixel(i, y0+y, QtCore.Qt.color0)
			for i in range(x0-x,x0+x+1):		
				l[y0-y][i] = True
				im.setPixel(i, y0-y, QtCore.Qt.color0)
			for i in range(x0-y,x0+y+1):
				l[y0+x][i] = True
				im.setPixel(i, y0+x, QtCore.Qt.color0)
			for i in range(x0-y,x0+y+1):
				l[y0-x][i] = True
				im.setPixel(i, y0-x, QtCore.Qt.color0)
			for i in range(x0-radius, x0+radius+1):
				l[y0][i] = True
				im.setPixel(i, y0, QtCore.Qt.color0)
		return l, im

def matrixToString(m):

	s = ""
	for i in m:
		for j in i:
			if j: s += chr(1)
			else: s += chr(0)
	return s

def printMatrix(m):
	for row in m:
		print(" ".join([str(x) for x in row]))
