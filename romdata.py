#!/usr/bin/env python3

from romdatalib import clrmamepro
from romdatalib.RomData import RomData
import json
import sys

def help ():
	program = "romdata.py"
	print ("""usage: """ + program + """ <command> [<document] [<args>]

The most commonly used """ + program + """ commands are:
   list       List all the IDs of the given document
   merge      Merge the second ID into the first one
   search     List IDs containing the given word""")

def list_ids (args):
	if len (args) == 0:
		print ("The document argument is missing.")
		return
	
	romdata_doc = RomData (args[0])
	
	if romdata_doc:
		games = romdata_doc.games ()
		games.sort ()
		for id in games:
			print (id)

def merge (args):
	if len (args) == 0:
		sys.stderr.write ("The document argument is missing.\n")
		return
	if len (args) == 1:
		sys.stderr.write ("An argument is missing.\n")
		return
	
	romdata_doc = RomData (args[0])
	
	if romdata_doc:
		id1 = args[1]
		id2 = args[2]
		
		if not id2 in romdata_doc:
			print ("The ID", id2, "doesn't exists.")
			return
		
		if len (romdata_doc[id2]) == 0:
			return
		
		romdata_doc.merge_ids (id1, id2)
		
		#fd = open(args[0], 'w')
		#fd.write (str (romdata_doc))
		#fd.close ()
	
	return romdata_doc

def search (args):
	if len (args) == 0:
		print ("The document argument is missing.")
		return
	if len (args) == 1:
		print ("An argument is missing.")
		return
	
	romdata_doc = RomData (args[0])
	
	if romdata_doc:
		search = args[1]
		
		games = romdata_doc.games ()
		games.sort ()
		for id in games:
			if search in id:
				print (id)

def merge_documents (romdata_doc1, romdata_doc2):
	romdata_doc1 = RomData (romdata_doc1)
	romdata_doc2 = RomData (romdata_doc2)
	romdata_doc1.merge_romdata (romdata_doc2)
	
	return romdata_doc1

def clrmamepro_to_romdata (clrmamepro_doc):
	romdata_doc = RomData()
	
	entries = clrmamepro.parse (clrmamepro_doc)
	
	if "game" in entries:
		# For each game entry in the TOSEC document
		for game in entries["game"]:
			rom = clrmamepro.game_to_rom (game, entries)
			game_id = RomData.name_to_id (rom["title"])
			
			romdata_doc.add_rom (game_id, rom["crc"], rom["md5"], rom["sha1"], rom["size"])
	return romdata_doc

if __name__ == "__main__":
	args = sys.argv[1:]
	
	if len (args) == 0:
		print ("""Run "romdata help" for command list""")
	
	else:
		command = args[0]
		args = args[1:]
		
		if command == "help":
			help ()
		
		elif command == "list":
			list_ids (args)
		
		elif command == "merge":
			print (merge (args))
		
		elif command == "mergedocs":
			if len (args) < 2:
				print ("Arguments are missing.")
			else:
				print (merge_documents (args[0], args[1]))
		
		elif command == "search":
			search (args)
		
		elif command == "clrmamepro":
			if len (args) == 0:
				print ("The document argument is missing.")
			else:
				clrmamepro_doc = args[0]
				print (clrmamepro_to_romdata (clrmamepro_doc))
		
		else:
			print ("Unknown command:", command)
			print ("Use the help command for help.")

