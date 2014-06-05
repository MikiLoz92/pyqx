#!/usr/bin/env python
#coding: utf-8


def enum(**named_values):
	return type('Enum', (), named_values)

Tools = enum( Selection=0, MagicWand=1, Pencil=2, Eraser=3, ColorPicker=4, Fill=5, Gradient=6, Exchange=7 )