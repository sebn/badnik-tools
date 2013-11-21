#!/usr/bin/env python3

from romdatalib import romdata
import json
import sys

def open_romdata_doc (document):
	pass

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
	
	romdata_doc = romdata.open_romdata (args[0])
	
	if romdata_doc:
		romdata_doc = romdata.romdata_from_clrmame (romdata_doc, [])
		ids = list (romdata_doc.keys())
		ids.sort ()
		for id in ids:
			print (id)

def merge (args):
	if len (args) == 0:
		sys.stderr.write ("The document argument is missing.\n")
		return
	if len (args) == 1:
		sys.stderr.write ("An argument is missing.\n")
		return
	
	romdata_doc = romdata.open_romdata (args[0])
	
	if romdata_doc:
		romdata_doc = romdata.romdata_from_clrmame (romdata_doc, [])
		id1 = args[1]
		id2 = args[2]
		
		if not id2 in romdata_doc:
			print ("The ID", id2, "doesn't exists.")
			return
		
		if len (romdata_doc[id2]) == 0:
			return
		
		romdata.romdata_merge_ids (romdata_doc, id1, id2)
		
		fd = open(args[0], 'w')
		
		fd.write (json.dumps(romdata_doc, sort_keys=True, indent=4, separators=(',', ': ')))
		
		fd.close ()

def search (args):
	if len (args) == 0:
		print ("The document argument is missing.")
		return
	if len (args) == 1:
		print ("An argument is missing.")
		return
	
	romdata_doc = romdata.open_romdata (args[0])
	
	if romdata_doc:
		romdata_doc = romdata.romdata_from_clrmame (romdata_doc, [])
		search = args[1]
		
		ids = list (romdata_doc.keys())
		ids.sort ()
		for id in ids:
			if search in id:
				print (id)
			elif romdata.edit_distance (search, id) < 5:
				print (id)

if __name__ == "__main__":
	args = sys.argv[1:]
	
	if len (args) == 0:
		print ("y'a pas de commande")
	
	else:
		command = args[0]
		args = args[1:]
		
		if command == "help":
			help ()
		
		elif command == "list":
			list_ids (args)
		
		elif command == "merge":
			merge (args)
		
		elif command == "search":
			search (args)
		
		else:
			print ("Unknown command:", command)
			print ("Use the help command for help.")

