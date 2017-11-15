"""
Scrapes movie data from IMdB using BeautifulSoup
"""
import urllib
from bs4 import BeautifulSoup

def load_page(url):
	""" return BS object from the given url """
	page = urllib.request.urlopen(url)
	return BeautifulSoup(page, 'html.parser')

def good_imdb_url(url):
	""" check if url is valid (i.e. from imdb) """
	o = urllib.parse.urlparse(url)
	return urllib.parse.urlparse(url).netloc == 'www.imdb.com'

def movie_info_from_soup(soup):
	""" gets the movie title, year, and poster url from a BS object
		return as a dict """
	info = soup.find('h1', itemprop='name')
	title = info.contents[0].strip()
	year = int(info.find(id='titleYear').a.text)
	poster_div = soup.find(class_='poster')
	poster_url = poster_div.find('img')['src']
	movie_info = {'title':title,
			'year':year,
			'poster_url':poster_url}
	return movie_info

def movie_info_from_url(url):
	""" check if url is appropriate. if yes, scrape title, year, poster url,
		return as a dict """
	if not good_imdb_url(url):
		return None
	soup = load_page(url)
	return movie_info_from_soup(soup)

def download_image(url, filename):
	""" download an image from a url and save it to a file """
	with urllib.request.urlopen(url) as response, open(filename, 'wb') as f:
		data = response.read()
		f.write(data)
