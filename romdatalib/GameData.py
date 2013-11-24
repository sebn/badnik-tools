#!/usr/bin/env python3

from unidecode import unidecode
import re
import json

class GameData:
	def __init__(self, gamedata_doc = None):
		
		# Set _gamedata
		if gamedata_doc:
			fd = None
			try:
				fd = open(gamedata_doc, 'r')
				self._gamedata = json.loads (fd.read ())
			except IOError:
				sys.stderr.write ("\"" + gamedata_doc + "\" doesn't exists.\n")
				self._gamedata = {}
			except ValueError:
				sys.stderr.write ("The document \"" + gamedata_doc + "\" isn't a GameData document.\n")
				self._gamedata = {}
			finally:
				if fd:
					fd.close ()
		else:
			self._gamedata = {}
		
		# TODO check if self._gamedata is a valid GameData document, not just a valid JSON document
	
	def __str__(self):
		return json.dumps(self._gamedata, sort_keys=True, indent=4, separators=(',', ': '))
	
	def __contains__(self, game_id):
		return game_id in self._gamedata
	
	def __getitem__(self, game_id):
		return self._gamedata[game_id]
	
	def __delitem__(self, game_id):
			del self._gamedata[game_id]
	
	def __iter__(self):
			return iter (self._gamedata)
	
	def __len__(self):
			return len (self._gamedata)
	
	def _init_game (self, game_id):
		if not game_id in self._gamedata:
			self._gamedata[game_id] = {
				"title": None,
				"description": None,
				"developers": [],
				"genres": [],
				"screenshots": [],
				"players": { "min": 0, "max": 0 },
				"versions": {},
				"tags": []
			}
	
	def _init_game_version (self, game_id, version):
		self._init_game (game_id)
		if not version in self._gamedata[game_id]["versions"]:
			self._gamedata[game_id]["versions"][version] = {
				"title": None,
				"publisher": None,
				"release_date": { "year": None, "month": None, "day": None },
				"cover": { "front": None, "back": None, "side": None }
			}
			
	
	def games(self):
		return list (self._gamedata.keys ())
	
	def set_title (self, game_id, title):
		self._init_game (game_id)
		self._gamedata[game_id]["title"] = title
	
	def get_title (self, game_id):
		if game_id in self._gamedata:
			return self._gamedata[game_id]["title"]
		else:
			return None
	
	def add_developer (self, game_id, developer):
		self._init_game (game_id)
		if not developer in self._gamedata[game_id]["developers"]:
			self._gamedata[game_id]["developers"].append (developer)
	
	def add_genre (self, game_id, genre):
		self._init_game (game_id)
		if not genre in self._gamedata[game_id]["genres"]:
			self._gamedata[game_id]["genres"].append (genre)
	
	def add_screenshot (self, game_id, screenshot):
		if screenshot:
			self._init_game (game_id)
			if not screenshot in self._gamedata[game_id]["screenshots"]:
				self._gamedata[game_id]["screenshots"].append (screenshot)
	
	def set_players (self, game_id, min_players, max_players = 0):
		self._init_game (game_id)
		# TODO check if min_players and max_players are valid values
		self._gamedata[game_id]["players"]["min"] = min_players
		self._gamedata[game_id]["players"]["max"] = max (min_players, max_players)
	
	def add_tag (self, game_id, tag):
		self._init_game (game_id)
		if not tag in self._gamedata[game_id]["tags"]:
			self._gamedata[game_id]["tags"].append (tag)
	
	def set_version_title (self, game_id, version, title):
		self._init_game_version (game_id, version)
		self._gamedata[game_id]["versions"][version]["title"] = title
	
	def get_version_title (self, game_id, version):
		if contains_version (game_id, version):
			return self._gamedata[game_id]["versions"][version]["title"]
		else:
			return None
	
	def set_version_publisher (self, game_id, version, publisher):
		self._init_game_version (game_id, version)
		self._gamedata[game_id]["versions"][version]["publisher"] = publisher
	
	def set_version_release_date (self, game_id, version, year, month = None, day = None):
		self._init_game_version (game_id, version)
		self._gamedata[game_id]["versions"][version]["release_date"]["year"] = year
		self._gamedata[game_id]["versions"][version]["release_date"]["month"] = month
		self._gamedata[game_id]["versions"][version]["release_date"]["day"] = day
	
	def set_version_cover (self, game_id, version, cover_front, cover_back = None, cover_side = None):
		self._init_game_version (game_id, version)
		self._gamedata[game_id]["versions"][version]["cover"]["front"] = cover_front
		self._gamedata[game_id]["versions"][version]["cover"]["back"] = cover_back
		self._gamedata[game_id]["versions"][version]["cover"]["side"] = cover_side
	
	def contains_version (self, game_id, version):
		return game_id in self._gamedata and version in self._gamedata[game_id]["versions"]

