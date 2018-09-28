#-*- coding: utf-8 -*-

import urllib, http.cookiejar
from bs4 import BeautifulSoup
from configparser import ConfigParser
import re
import os, sys, getopt

def getHTML(url):
	cj = http.cookiejar.LWPCookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)) 
	urllib.request.install_opener(opener)
	
	params = urllib.parse.urlencode({})
	params = params.encode('utf-8')
	req = urllib.request.Request(url, params)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')
	res = opener.open(req)
	html = res.read()
	
	return html
	
def getTPTorrentLinks(html, matching_day):
	soup = BeautifulSoup(html, 'html.parser')
	
	# tr의 class=alt를 모두 얻는다.
	raw = soup.find(id='searchResult')
	# 첫번째 tr은 header부분이라 제외
	# 마지막 tr은 페이지 링크 부분이라 제외
	links = raw.find_all('tr')[1:-2]
	
	# 리스트 중 matching_day에 해당하는링크부분만 추출
	# Today 또는 Y-day (날짜는 뽑아내기 애매해서 무시함)
	torrent_links = []
	for link in links:
		tds = link.find_all('td')
#		print (link)
		#print(tds[1])
		# 두번째 td 에서 정해진 날짜 문자열이 포함되어 있는지 확인
		if tds[1].find(string=re.compile(matching_day)) != None:
		# 마그넷 링크는 두번째에 a href에 들어있음
#			print(tds[1])
			torrent_links.append(tds[1].find_all('a')[1]['href'])

	return torrent_links

def help():
	print ('''option is not enough.\nUsage: %s -c ConfigFilename
	''' % (sys.argv[0]))

if __name__ == '__main__':
	#설정 파일 옵션 확인
	try:
		opts, args = getopt.getopt(sys.argv[1:], "dc:")
	except getopt.GetoptError as err:
		print (str(err))
		help()
		sys.exit(1)

	config_file = ''
	debug_mode = False
	for opt, arg in opts:
		if opt == '-c':
			config_file = arg
		elif opt == '-d':
			debug_mode = True

	if config_file == '':
		help()
		sys.exit(1)

	#설정파일 읽기
	config = ConfigParser()
	config.read(config_file)

	URL = config.get('SETTING', 'URL')
	DAY = config.get('SETTING', 'DAY')
	HOST = config.get('SETTING', 'HOST')
	USERNAME = config.get('SETTING', 'USERNAME')
	PASSWORD = config.get('SETTING', 'PASSWORD')
	COMMAND = config.get('SETTING', 'COMMAND')

	lists = getTPTorrentLinks(getHTML(URL), DAY)

	for item in lists:
		if debug_mode == True:
			print ('debug mode')
			print (item)
		else:
			os.system ('%s %s --auth %s:%s --add "%s"' % (COMMAND, HOST, USERNAME, PASSWORD, item))
