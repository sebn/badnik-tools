#!/usr/bin/env python3

from unidecode import unidecode
import re
import json

class RomData:
	def __init__(self, romdata_doc = None):
		
		# Set _romdata
		if romdata_doc:
			fd = None
			try:
				fd = open(romdata_doc, 'r')
				self._romdata = json.loads (fd.read ())
			except IOError:
				sys.stderr.write ("\"" + romdata_doc + "\" doesn't exists.\n")
				self._romdata = {}
			except ValueError:
				sys.stderr.write ("The document \"" + romdata_doc + "\" isn't a ROMData document.\n")
				self._romdata = {}
			finally:
				if fd:
					fd.close ()
		else:
			self._romdata = {}
	
	def __str__(self):
		return json.dumps(self._romdata, sort_keys=True, indent=4, separators=(',', ': '))
	
	def __contains__(self, game_id):
		return game_id in self._romdata
	
	def __getitem__(self, game_id):
		return self._romdata[game_id]
	
	def __delitem__(self, game_id):
			del self._romdata[game_id]
	
	def __iter__(self):
			return iter (self._romdata)
	
	def __len__(self):
			return len (self._romdata)
	
	def games(self):
		return list (self._romdata.keys ())
	
	def get_id_from_fingerprint (self, fingerprint, hash_type):
		fingerprint = fingerprint.lower ()
		for game_id in self.games():
			for rom in self._romdata[game_id]:
				if hash_type in rom:
					if rom[hash_type].lower () == fingerprint:
						return game_id
		return None
	
	def add_rom (self, game_id, crc, md5, sha1, size):
		if not game_id in self._romdata:
			self._romdata[game_id] = []
		
		# TODO check if the rom already exists before to add it
		self._romdata[game_id].append ({ "crc": crc, "md5": md5, "sha1": sha1, "size": size })
	
	def remove_id (self, game_id):
		self._romdata.pop (game_id, None)
	
	def merge_ids (self, to_fill, to_remove):
		if not to_fill in self._romdata:
			self._romdata[to_fill] = []
		
		for game in self._romdata[to_remove]:
			self.add_rom (to_fill, game["crc"], game["md5"], game["sha1"], game["size"])
		
		self.remove_id (to_remove)
	
	# TODO à tester
	def merge_romdata (self, other_romdata):
		
		# Set the ID table, used to automatically check (and then merge) if roms are from the same game
		id_table = {}
		for game in self.games ():
			id_table[game] = game
		
		for game_id in other_romdata.games ():
			for rom in other_romdata[game_id]:
				# Init the new entry in the ID table
				if not game_id in id_table:
					id_table[game_id] = game_id
				
				while (game_id != id_table[game_id]):
					game_id = id_table[game_id]
				
				# Init the new entry in the ROMData doc
				if not game_id in self._romdata:
					self._romdata[game_id] = []
				
				# The game could exist with a different ID
				existing_game_id = self.get_id_from_fingerprint (rom["md5"], "md5")
				if existing_game_id != None and existing_game_id != game_id:
					# Merge the ducplicated id entries
					self.merge_ids (existing_game_id, game_id)
					id_table[game_id] = existing_game_id
					game_id = existing_game_id
				
				self.add_rom (game_id, rom["crc"], rom["md5"], rom["sha1"], rom["size"])
	
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
