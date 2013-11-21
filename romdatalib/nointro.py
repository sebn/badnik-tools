#!/usr/bin/python3
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

def is_nointro (parsed_doc):
	if "clrmamepro" in parsed_doc:
		doc = parsed_doc["clrmamepro"][0]
		
		if "comment" in doc:
			return "no-intro" in doc["comment"]
	
	return False

def split_game_title(game):
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

