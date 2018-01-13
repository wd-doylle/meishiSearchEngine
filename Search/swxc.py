#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys


reload(sys)
sys.setdefaultencoding('utf-8')


def readin(filename):
	file = open(filename, 'r')
	lines = file.readlines()
	file.close()
	res = {}
	alist = []
	for line in lines:
		a, b, c = (line.strip()).split('|')
		tmp = ''
		if b:
			tmp = "【相宜】" + b
		if c:
			if tmp:
				tmp += '@【相克】' + c
			else:
				tmp = "【相克】" + c
		res[a] = tmp
		alist.append(a)
	return res, alist

def readin_msj(filename):
	file = open(filename, 'r')
	lines = file.readlines()
	file.close()
	res = {}
	alist = []
	for line in lines:
		try:
			a, b = (line.strip()).split('|', 2)
			res[a] = b.replace('\t','@')
			alist.append(a)
		except:
			pass
	return res, alist

