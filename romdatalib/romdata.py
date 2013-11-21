#!/usr/bin/env python3

from romdatalib import clrmamepro, tosec, nointro

from unidecode import unidecode
import json
import re
import sys

hash_func = "md5"

def edit_distance (src, dst):
	if not dst: return len(src)
	if not src: return len(dst)
	 
	return min(
		# Case 1
		(edit_distance(src[:-1], dst[:-1]) + (1, 0)[src[-1] == dst[-1]]),
		# Case 2
		(edit_distance(src[:-1], dst) + 1),
		# Case 3
		(edit_distance(src, dst[:-1]) + 1)
	)

def open_romdata (romdata_path):
	try:
		fd = open(romdata_path, 'r')
		romdata_doc = json.loads (fd.read ())
		fd.close ()
		return romdata_doc
	except IOError:
		sys.stderr.write ("\"" + romdata_path + "\" doesn't exists.\n")
	except ValueError:
		sys.stderr.write ("The document \"" + romdata_path + "\" isn't a ROMData document.\n")
	return None

def name_to_id (name):
	# Replace all special characters
	string = unidecode (name).lower ()
	
	# Replace all suits of characters other than a-z or 0-9 by a single hyphen
	string = re.sub ("[^a-z0-9]+", "-", string)
	
	# Remove hyphens at the beginning and the end of the string
	match = re.search ("^-?(.*?)-?$", string)
	if (match):
		string = match.group(1)
	
	return string

def _idtable_from_romdata (romdata_doc):
	idtable = {}
	
	for key in romdata_doc.keys ():
		idtable[key] = key
	
	return idtable

def romdata_id_from_fingerprint (romdata_doc, fingerprint, hash_type):
	fingerprint = fingerprint.lower ()
	for game_id in romdata_doc.keys():
		for rom in romdata_doc[game_id]:
			if hash_type in rom:
				if rom[hash_type].lower () == fingerprint:
					return game_id
	return None

def romdata_add_rom (romdata_doc, game_id, rom):
	# Check for double entries
	for game in romdata_doc[game_id]:
		if game[hash_func] == rom[hash_func]:
			for key in rom.keys():
				game[key] = rom[key]
			return romdata_doc
	
	romdata_doc[game_id].append (rom)
	return romdata_doc

def romdata_merge_ids (romdata_doc, to_fill, to_remove):
	if not to_fill in romdata_doc:
		romdata_doc[to_fill] = []
	
	for game in romdata_doc[to_remove]:
		romdata_doc = romdata_add_rom (romdata_doc, to_fill, game)
	romdata_doc.pop (to_remove, None)
	
	return romdata_doc

def game_to_rom (game, entries):
	rom = {}
	if tosec.is_tosec (entries):
		rom["title"], rom["revision"], rom["game_flags"], rom["rom_flags"] = tosec.split_game_title (game["name"])
	elif nointro.is_nointro (entries):
		rom["title"], rom["other_flags"], rom["type_flags"] = nointro.split_game_title (game["name"])
	else:
		rom["title"] = game["title"]
	
	for e in ("size", "crc", "md5", "sha1"):
		if e in game["rom"]:
			rom[e] = game["rom"][e].lower ()
	
	return rom

def romdata_from_clrmame (romdata_doc, clrmame_docs):
	id_table = _idtable_from_romdata (romdata_doc)
	
	for clrmamepro_doc in clrmame_docs:
		entries = clrmamepro.parse (clrmamepro_doc)
		
		if "game" in entries:
			# For each game entry in the TOSEC document
			for game in entries["game"]:
				rom = game_to_rom (game, entries)
				
				game_id = name_to_id (rom["title"])
				rom.pop ("title", None)
				
				# Init the new entry in the ID table
				if not game_id in id_table:
					id_table[game_id] = game_id
				
				while (game_id != id_table[game_id]):
					game_id = id_table[game_id]
				
				# Init the new entry in the ROMData doc
				if not game_id in romdata_doc:
					romdata_doc[game_id] = []
					
				# The game could exist with a different ID
				existing_game_id = romdata_id_from_fingerprint (romdata_doc, rom[hash_func], hash_func)
				if existing_game_id != None and existing_game_id != game_id:
					# Merge the ducplicated id entries
					romdata_doc = romdata_merge_ids (romdata_doc, existing_game_id, game_id)
					id_table[game_id] = existing_game_id
					game_id = existing_game_id
				
				romdata_doc = romdata_add_rom (romdata_doc, game_id, rom)
	return romdata_doc

if __name__ == "__main__":
	'''Arguments are the files to parse, the last one is the file to edit if it exists or the output file.'''
	import sys
	
	romdata_file = sys.argv[-1]
	docs = list (sys.argv)[1:-1]
	print (romdata_file)
	print (docs)
	#romdata_doc = romdata_from_clrmame ({}, docs)
	#print (json.dumps(romdata_doc, sort_keys=True, indent=4, separators=(',', ': ')))

