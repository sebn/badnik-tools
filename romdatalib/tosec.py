#!/usr/bin/env python3
#    tosec.py A Python module to use TOSEC data files as a SQLite database.
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
from romdatalib import clrmamepro

def is_tosec (parsed_doc):
	if "clrmamepro" in parsed_doc:
		doc = parsed_doc["clrmamepro"][0]
		
		if "description" in doc:
			return "TOSEC" in doc["description"]
	
	return False

def split_game_title(game):
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

