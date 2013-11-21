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

def game_to_rom (game, entries):
        rom = {}
        if is_tosec (entries):
                rom["title"], rom["revision"], rom["game_flags"], rom["rom_flags"] = split_tosec_game_title (game["name"])
        elif is_nointro (entries):
                rom["title"], rom["other_flags"], rom["type_flags"] = split_nointro_game_title (game["name"])
        else:
                rom["title"] = game["title"]
        
        for e in ("size", "crc", "md5", "sha1"):
                if e in game["rom"]:
                        rom[e] = game["rom"][e].lower ()
        
        return rom

def is_nointro (parsed_doc):
	if "clrmamepro" in parsed_doc:
		doc = parsed_doc["clrmamepro"][0]
		
		if "comment" in doc:
			return "no-intro" in doc["comment"]
	
	return False

def split_nointro_game_title(game):
	'''Return a tuple containg the game title, the game flags and the ROM flags'''
	title = ""
	type_flags = ""
	other_flags = ""
	result = re.match(r'''^(\[[^\(\)]*\])?\s*([^\(\)\[\]]+) (\(?[^\[\]]*\)?)''', game)
	if result:
		type_flags = result.group(1)
		title = result.group(2)
		other_flags = result.group(3)
	
	return (title, other_flags, type_flags)

def is_tosec (parsed_doc):
	if "clrmamepro" in parsed_doc:
		doc = parsed_doc["clrmamepro"][0]
		
		if "description" in doc:
			return "TOSEC" in doc["description"]
	
	return False

def split_tosec_game_title(game):
	'''Return a tuple containg the game title, the game flags and the ROM flags'''
	title = ""
	revision = ""
	game_flags = ""
	rom_flags = ""
	
	result = re.match(r'''^([^\(\)\[\]]+) .*?(\(?[^\[\]]*\)?)(\[?[^\(\)]*\]?)''', game)
	if result:
		title = result.group(1)
		game_flags = result.group(2)
		rom_flags = result.group(3)
	
	result = re.match ("^(.*?) Rev (.*?)$", title)
	if result:
		title = result.group (1)
		revision = result.group (2)
	
	result = re.match ("^(.*?) (v\d*\..*?)$", title)
	if result:
		title = result.group (1)
		revision = result.group (2)
	
	return (title, revision, game_flags, rom_flags)

def datefromiso(isoformat):
	date = isoformat.split('-')
	return datetime.date(int(date[0]), int(date[1]), int(date[2]))

