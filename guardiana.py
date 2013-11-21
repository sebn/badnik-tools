import urllib
from html.parser import HTMLParser
import re
from bs4 import BeautifulSoup

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

def get_game_data (url):
	"""Get a GameData object for the corresponding Guardiana URL."""
	
	flags = ["error", "JP", "EU", "US", "CN", "BR", "pirate", "KR", "AU", "FR", "BE", "ES", "GB", "IT", "PT", "SE", "CA", "LU", "unknown", "not-understood"]
	
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
	general_info_table = soup.find("table", {"class": "MDGD_GamesInfos"})
	version_list = soup.find_all("div", {"class": "versionFiche"})
	
	game_data = {}
	
	result = re.findall ("<div.*?databaseInfosDesc.*?>(.+?)</div>\s*<div.*?databaseInfosContent.*?>(.+?)</div>", str (general_info_table))
	for info in result:
		game_data[info[0]] = info [1]
	
	game_data["players"] = general_info_table.find ("span", {"class": "GamePlayers1"}).get_text ()
	
	versions = []
	for v in version_list:
		version = {}
		
		# Title
		version["title"] = v.find ("span", {"class": "MDGDVersionTitle"}).get_text ()
		
		# Local title
		local_title = v.find ("td", {"class": "TextCenter", "colspan": "2"}).get_text ()
		if local_title:
			version["local_title"] = local_title
		
		# Country
		result = re.search("/img/flags/(\d+).gif", str (v))
		if result:
			flag_nbr = int (result.group(1))
			if flag_nbr < len (flags):
				version["country"] = flags[flag_nbr]
			else:
				version["country"] = flags[0]
		else:
			version["country"] = flags[0]
		
		# Cover
		covers_soup = v.find ("div", {"class": "alternatecoverbox"})
		covers = {}
		side = covers_soup.find ("img", {"alt": "Side / SpinCard"})
		if side and "src" in side.attrs:
			covers["side"] = side["src"]
		front = covers_soup.find ("img", {"alt": "Front"})
		if front and "src" in front.attrs:
			covers["front"] = front["src"]
		back = covers_soup.find ("img", {"alt": "Back"})
		if back and "src" in back.attrs:
			covers["back"] = back["src"]
		full = covers_soup.find ("a", {"class": "fancybox_img"})
		if full and "href" in full.attrs:
			covers["full"] = full["href"]
		version["covers"] = covers
		
		# Serial number, barcode, publisher, release date...
		result = re.findall ("<div.*?databaseInfosDesc.*?>(.+?)</div>\s*<div.*?databaseInfosContent.*?>(.+?)</div>", str (v))
		for info in result:
			version[info[0]] = info [1]
		
		versions.append (version)
	
	game_data["versions"] = versions
	
	return game_data

if __name__ == "__main__":
	from romdatalib.RomData import RomData
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
	
	print ('Downloading game list')
	game_list = get_game_list (systems[system])
	
	game_data = {}
	i = 1
	n = str (len (game_list))
	for game in game_list:
		print ('Downloading game data ' + str(i).rjust(len (n)) + ' / ' + n + ' : ' + game["title"][0])
		game_id = RomData.name_to_id (game["title"][0])
		try:
			game_data[game_id] = get_game_data (game["url"])
		except URLError:
			sys.stderr.write ("The program can't download " + game["url"] + ".\n")
			sys.stderr.write ("Aborting.\n")
			sys.exit (1)
		i = i+1
	
	document = str (json.dumps(game_data, sort_keys=True, indent=4, separators=(',', ': ')))
	
	fd = open(output, 'w')
	fd.write (document)
	fd.close ()

