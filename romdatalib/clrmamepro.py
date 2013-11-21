#!/usr/bin/python3
#    clrmamepro.py A Python module to handle clrmamepro files.
#    Copyright (C) 2013 Adrien Plazas
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    
#    Adrien Plazas <mailto:kekun.plazas@laposte.net>

import re

def _get_words (filename):
	input = open(filename, "r")
	data = input.read()
	result = re.split(r'''((?:[^ \n\r\t"]|"[^"]*")+)''', data)
	
	return result[1::2]

def _word_cleanup (word):
	result = re.match ("\"(.*?)\"", word)
	if result:
		return result.group(1)
	else:
		return word

def _parse_from_words (words):
	'''Transform a list of words into a dictionary of entry list, whose keys are the entry's tag and whose content is nested dictionaries.'''
	entries = {}
	entry = {}
	
	last_path = ""
	path = ""
	tag = None
	for word in words:
		if last_path != "" and path == "":
			# Add the parsed entry to the list
			for key in entry.keys ():
				# If the key doesn't exsist in entries, create it
				if not key in entries:
					entries[key] = []
				# Add the parsed entry to the corresponding list
				entries[key].append (entry[key])
			entry = {}
		else:
			last_path = path
		if not tag:
			if word == ")":
				# Go up in the dictionaries tree
				splitted_path = path.split(" ")
				path = ""
				for element in splitted_path[:-1]:
					if path == "":
						path = element
					else:
						path = path + " " + element
			else:
				tag = word
		else:
			if word == "(":
				# Add a new depth in the dictionaries tree
				dict = entry
				for element in path.split(" "):
					if element != "":
						dict = dict[element]
				dict[tag] = {}
				if path == "":
					path = tag
				else:
					path = path + " " + tag
			else:
				# Add a new element
				dict = entry
				for element in path.split(" "):
					dict = dict[element]
				dict[tag] = _word_cleanup (word)
			tag = None
	
	return entries

def parse (filename):
	return _parse_from_words (_get_words (filename))

