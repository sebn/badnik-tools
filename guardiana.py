import urllib
from html.parser import HTMLParser
import re
from bs4 import BeautifulSoup
from romdatalib.GameData import GameData
from romdatalib.RomData import RomData
from urllib.error import URLError

#
# Utility tables
#

systems = {
	"master-system": "Master%20System",
	"game-gear": "Game%20Gear",
	"mega-drive": "Mega%20Drive",
	"mega-cd": "Mega%20CD",
	"sega-modem": "SEGA%20MODEM",
	"laseractive-mega-ld": "LaserActive%20Mega%20LD",
	"sega-pico": "SEGA%20PICO",
	"mega-drive-32x": "Mega%20Drive%2032X",
	"megacd-32x": "MegaCD-32X",
	"dreamcast": "Dreamcast",
	"naomi": "NAOMI",
	"mega-tech": "Mega-Tech",
}

flags = [
	"error",
	"JP",
	"EU",
	"US",
	"CN",
	"BR",
	"unlicenced",
	"KR",
	"AU",
	"FR",
	"BE",
	"ES",
	"GB",
	"IT",
	"PT",
	"SE",
	"CA",
	"LU",
	"unknown",
	"homebrew"
]

#
# Utility functions
#

def is_string_null (string):
	string = html_get_text (string).lower ()
	null = bool (not string or string == "" or string == "unknown")
	return null

def html_get_text (html):
	text = "".join (re.split ("<.*?>", html))
	
	return text

def split_date (d_m_y_date):
	date = re.split('\D', d_m_y_date, maxsplit=2)
	date.reverse ()
	
	int_date = []
	for s in date:
		int_date.append (int (s))
	
	while len (int_date) < 3:
		int_date.append (None)
	
	return int_date

#
# Core Guardiana functions
#

def get_game_list (system):
	"""List all the games on Guardiana for a given system."""
	
	response = urllib.request.urlopen ("http://www.guardiana.net/MDG-Database/Complete-List/" + system + "/")
	
	doc = response.read ()
	
	soup = BeautifulSoup(doc)
	html_game_list = soup.find("div", {"id": "MDGD_FullList_Box"})
	
	game_list = re.findall ("""» <a href="(.+?)">(.+?)</a><br/>(?:<em>)?(.*?)(?:</em>)?<br/>""", str (html_game_list))
	
	game_dict_list = []
	
	for game in game_list:
		game_dict = {'url': "http://www.guardiana.net" + game[0], 'title': [ ]}
		
		# Clean up the URL and add it
		result = re.search ("(.*?)\?PHPSESSID=.*?", game[0])
		if result:
			game_dict['url'] = "http://www.guardiana.net" + result.group(1)
		else:
			game_dict['url'] = "http://www.guardiana.net" + game[0]
		
		# Unescape the HTML entities from titles and add them
		pars = HTMLParser()
		game_dict['title'].append (pars.unescape (game[1]))
		game_dict_list.append (game_dict)
	
	return game_dict_list

def add_game_data_from_url (game_data, url):
	"""Get a GameData object for the corresponding Guardiana URL."""
	
	#
	# Download and read the page from Guardiana
	#
	
	response = None
	i = 0
	while response == None  and i < 5:
		try:
			response = urllib.request.urlopen (url)
		except URLError:
			pass
	
	if response == None:
		raise URLError
	
	doc = response.read ()
	soup = BeautifulSoup(doc)
	
	#
	# Get the common game data
	#
	
	general_info_table = soup.find("table", {"class": "MDGD_GamesInfos"})
	
	common = { "title": None, "developer": None, "genre": None, "players": [0, 0], "tags": [] }
	
	result = re.findall ("<\s*div.*?databaseInfosDesc.*?>(.+?)<\s*/\s*div\s*>\s*<\s*div.*?databaseInfosContent.*?>(.+?)<\s*/\s*div\s*>", str (general_info_table))
	
	for info in result:
		key = info[0].lower()
		if key == "common title":
			common["title"] = info[1]
		elif key == "theme":
			for tag in re.split ("\s*,\s*", info[1].strip().lower ()):
				if not tag in common["tags"]:
					common["tags"].append (tag)
		elif key == "developer":
			if not is_string_null (info[1]):
				common["developer"] = html_get_text (info[1])
		elif key == "genre":
			if not is_string_null (info[1]):
				common["genre"] = info[1]
	
	# Set the game's players number
	game_players = general_info_table.find ("span", {"class": "GamePlayers1"}).get_text ()
	if game_players:
		game_players = game_players.split ('-', 1)
		if len (game_players) > 1:
			common["players"][0] =  int (game_players[0])
			common["players"][1] =  int (game_players[1])
		else:
			common["players"][0] =  int (game_players[0])
	
	# The script can't do anything without the game's title
	if not common["title"]:
		return False
	
	# Get the game's ID from its title
	game_id = RomData.name_to_id (common["title"])
	
	#
	# Set the common game data
	#
	
	game_data.set_title (game_id, common["title"])
	game_data.set_developer (game_id, common["developer"])
	game_data.set_genre (game_id, common["genre"])
	game_data.set_players (game_id, common["players"][0], common["players"][1])
	for tag in common["tags"]:
		game_data.add_tag (game_id, tag)
	
	#
	# Get the versions' data
	#
	
	version_list = soup.find_all("div", {"class": "versionFiche"})
	
	for v in version_list:
		# Country
		v_country = flags[0]
		result = re.search("/img/flags/(\d+).gif", str (v))
		if result:
			flag_nbr = int (result.group(1))
			if flag_nbr < len (flags):
				v_country = flags[flag_nbr]
		
		if game_data.contains_version (game_id, v_country):
			continue
		
		#
		# Set the version's title
		#
		
		# Get the version's title
		v_title = v.find ("span", {"class": "MDGDVersionTitle"}).get_text ()
		result = re.match ("(.*?)\s*\((.*?)\)", v_title)
		if result:
			v_title = result.group (1)
		
		# Get the local title
		v_local_title = v.find ("td", {"class": "TextCenter", "colspan": "2"}).get_text ()
		if not is_string_null (v_local_title):
			v_title = v_local_title
		game_data.set_version_title (game_id, v_country, v_local_title)
		
		# If the version's title is the same as the common title, it should be null
		if common["title"] == v_title:
			v_title = None
		
		game_data.set_version_title (game_id, v_country, v_title)
		
		#
		# Set the version's cover
		#
		
		covers_soup = v.find ("div", {"class": "alternatecoverbox"})
		v_cover = { "front": None, "back": None, "side": None }
		
		side = covers_soup.find ("img", {"alt": "Side / SpinCard"})
		if side and "src" in side.attrs:
			v_cover["side"] = side["src"]
		
		front = covers_soup.find ("img", {"alt": "Front"})
		if front and "src" in front.attrs:
			v_cover["front"] = front["src"]
		
		back = covers_soup.find ("img", {"alt": "Back"})
		if back and "src" in back.attrs:
			v_cover["back"] = back["src"]
		
		game_data.set_version_cover (game_id, v_country, v_cover["front"], v_cover["back"], v_cover["side"])
		
		# Serial number, barcode, publisher, release date...
		result = re.findall ("<\s*div.*?databaseInfosDesc.*?>(.+?)<\s*/\s*div\s*>\s*<\s*div.*?databaseInfosContent.*?>(.+?)<\s*/\s*div\s*>", str (v))
		for info in result:
			key = info[0].lower()
			if key == "publisher":
				if not is_string_null (info[1]):
					game_data.set_version_publisher (game_id, v_country, html_get_text (info[1]))
			
			# Release date
			elif key == "release date":
				if not is_string_null (info[1]):
					v_date = split_date (info[1])
					game_data.set_version_release_date (game_id, v_country, v_date [0], v_date [1], v_date [2])
	
	return True

def get_game_data_from_guardiana ():
	print ('Downloading game list')
	game_list = get_game_list (systems[system])
	
	game_data = GameData ()
	i = 1
	n = str (len (game_list))
	for game in game_list:
		print ('Downloading game data ' + str(i).rjust(len (n)) + ' / ' + n + ' : ' + game["title"][0])
		
		try:
			while not add_game_data_from_url (game_data, game["url"]):
				pass
		except URLError:
			sys.stderr.write ("The program can't download " + game["url"] + ".\n")
			sys.stderr.write ("Aborting.\n")
			sys.exit (1)
		i = i+1
	
	return game_data

if __name__ == "__main__":
	import json
	import sys, argparse
	
	parser = argparse.ArgumentParser(description='Dump game informations from guardiana.net.')
	parser.add_argument('system', metavar='system', nargs=1, help='the system to download', choices=systems.keys())
	parser.add_argument('-o', '--output', dest='output', nargs=1, help='the file wich will receive the output')
	
	args = parser.parse_args()
	
	system = args.system[0]
	if args.output:
		output = args.output[0]
	else:
		output = system + '.gamedata.json'
	
	game_data = get_game_data_from_guardiana ()
	
	fd = open(output, 'w')
	fd.write (str (game_data))
	fd.close ()

