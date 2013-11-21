import urllib
from html.parser import HTMLParser
import re
from bs4 import BeautifulSoup

from romdatalib import romdata

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
	
	response = urllib.request.urlopen (url)
	
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
			print (local_title)
		
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
	import json
	
	game_data = get_game_data ("http://www.guardiana.net/MDG-Database/Mega%20Drive/Sonic%20The%20Hedgehog%202/")
	
	print (json.dumps(game_data, sort_keys=True, indent=4, separators=(',', ': ')))

