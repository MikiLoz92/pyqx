#!/usr/bin/env python
#coding: utf-8

import os
import ConfigParser

class Language:

	def __init__(self, langCode, langName, d):

		self.code = langCode
		self.name = langName
		self.dict = d

	def __getitem__(self, item):

		return self.dict[item]

class TDatabase:

	def __init__(self):
		
		self.d = {}
		self.langAvailable = []

		cp = ConfigParser.ConfigParser()
		l = os.listdir("lang")
		for i in l:
			cp.read("lang/" + i)
			langname = cp.get("_lang", "name").decode("utf-8")
			d2 = {}
			for j in cp.sections()[1:]: # Sin la sección _lang
				d3 = {}
				for k, l in cp.items(j):
					d3[k] = l
				d2[j] = d3
			lang = Language(i, langname, d2)
			self.d[i] = lang
			self.langAvailable.append(i)

		self.langNum = len(self.d.keys())

	def getText(self, lang, sect, ident):

		return self.d[lang][sect][ident]