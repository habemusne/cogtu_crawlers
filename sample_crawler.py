#!/usr/bin/env python
#encoding: utf8
# -*- coding: encoding -*-
import mechanize
import sys,re,os
import urllib2
from urllib2 import HTTPError
from time import sleep
from lxml.html import fromstring
import lxml.html
from bs4 import BeautifulSoup
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebPage


# define login credentials here
LOGIN_USERNAME = 'itisnanful1@gmail.com'
LOGIN_PASSWORD = '1111111111'

TAG_TABLE_FILE = './t_tag.txt'
ALBUM_TABLE_FILE = './t_album.txt'
PHOTO_TABLE_FILE = './t_photo.txt'
USER_TABLE_FILE = './t_user.txt'
COMMENT_TABLE_FILE = './t_comment.txt'
ghost = Ghost()

# Match a number that has more than 1 digit and is after
#  'http://tuchong.com/'' and is before a '/'. This number
#  is the album id
REGEX_ALBUMID_FROM_URL = r'\/([0-9]{1,})\/'
REGEX_AUTHORID_FROM_URL = r'\/([0-9]{1,})\/$'
REGEX_PHOTOID_FROM_URL = r'f\/([0-9]{1,})\.'
def handleEmptyTagDict(br, theDict):
	return fetchCommonTags(br)

def handleEmptyAlbumLinkDict(br, theDict):
	return {}

def handleEmptyTagPageDict(br, theDict):
	return {}

def initializeDict(br, listFileName, handleFunc):
	theDict = {}
	if os.path.isfile(listFileName) and os.stat(listFileName).st_size > 0:
		with open(listFileName, "r") as ins:
			for line in ins:
				if len(line.split(",")) == 1:
					continue
				else:
					theDict[line.split(",")[0]] = line.split(",")[1].strip()
	else:
		theDict = handleFunc(br, theDict)
	return theDict

def finalizeDict(theDict, listFileName):
	with open(listFileName, "w") as ins:
		for key in theDict:
			ins.write(str(key) + ',' + str(theDict[key]) + '\n')

# fetchByAlbumLink()
# @param: br - browser
#         album_link - link assigned by tuchong.com for each album
#         albumlist - list of albums to be fetched
# @return: 
def fetchByAlbumLink(br, album_link, visited_album_links):
	print album_link
	try:
		page = br.open(album_link)
	except HTTPError:
		print 'HTTPError at ' + album_link
		return

	

	doc = lxml.html.document_fromstring(page.read())

	match = re.compile(REGEX_ALBUMID_FROM_URL).findall(album_link)
	if len(match) == 2:
		albumID = re.search(REGEX_ALBUMID_FROM_URL, album_link).group(2)
	else:
		albumID = re.search(REGEX_ALBUMID_FROM_URL, album_link).group(1)

	albumAuthorID = ""
	albumPostTime = ""
	albumTitle = ""
	albumDesc = ""
	albumTags = []
	photoLinks = []
	photoIDs = []
	favoriteAuthorIDs = []
	shareNum = ""
	commentAuthor = []
	commentContent = []
	commentTime = []
	commentPhoto = []
	commentLikes = []

	info_block = doc.xpath(
		'//div[@class="container container-default"]/main/div[@class="post-wrapper"]')[0]

	albumAuthorHTML = info_block.xpath(
		'div[@class="post-header-wrapper"]/hgroup/a/@data-site-id')
	albumPostTimeHTML = info_block.xpath(
		'div[@class="post-header-wrapper"]/hgroup/time/@datetime')
	albumTitleHTML = info_block.xpath('div[@class="post-content"]/h1')
	albumDescHTML = info_block.xpath('div[@class="post-content"]/article')
	tagsHTML = info_block.xpath(
		'div[@class="post-content"]/div[@class="post-tag"]/a')
	photosHTML = doc.xpath(
		'//div[@class="container container-default"]/'\
		'main/div/div[@class="figures-wrapper"]/figure')
	favoriteHTML = doc.xpath(
		'//div[@class="container container-default"]/aside/'\
		'section[@class="post-favorites clearfix widget"]/ul/li')
	commentHTML = doc.xpath(
		'//div[@class="container container-default"]/main/'
		'section[@class="comments-wrapper post-comments with-bg"]/ul/li')

	if albumAuthorHTML != None and len(albumAuthorHTML) != 0:
		albumAuthorID = albumAuthorHTML[0]
	if albumPostTimeHTML != None and len(albumAuthorHTML) != 0:
		albumPostTime = albumPostTimeHTML[0]
	if albumTitleHTML != None and len(albumTitleHTML) != 0:
		albumTitle = albumTitleHTML[0].text_content()
	if albumDescHTML != None and len(albumDescHTML) != 0:
		albumDesc = albumDescHTML[0].text_content()
	if tagsHTML != None and len(tagsHTML) != 0:
		albumTags = [None] * len(tagsHTML)
		for i in range(0, len(tagsHTML)):
			albumTags[i] = tagsHTML[i].text_content()

	if photosHTML != None and len(photosHTML) != 0:
		photoLinks = [None] * len(photosHTML)
		photoIDs = [None] * len(photosHTML)
		for i in range(0, len(photosHTML)):
			photoLinks[i] = photosHTML[i].xpath('img/@src')[0]
			photoIDs[i] = re.search(REGEX_PHOTOID_FROM_URL,
				photoLinks[i]).group(1)

	if favoriteHTML != None and len(favoriteHTML) != 0:
		favoriteAuthorIDs = [None] * len(favoriteHTML)
		for i in range(0, len(favoriteHTML)):
			favoriteAuthorIDs[i] = favoriteHTML[i].xpath('a/@data-site-id')[0]
		shareNum = doc.xpath('//div[@class="container container-default"]/aside/'\
			'section[@class="post-favorites clearfix widget"]/h3')[0]\
			.text_content().split(u'人')[0]

	# print lxml.html.tostring(doc.xpath(
	# 	'//div[@class="container container-default"]/main/'
	# 	'section[@class="comments-wrapper post-comments with-bg"]/ul')[0])
	print doc.xpath('//a[@class="author-name user-anchor"]')
	if commentHTML != None and len(commentHTML) != 0:
		commentAuthor = [None] * len(commentHTML)
		commentContent = [None] * len(commentHTML)
		commentTime = [None] * len(commentHTML)
		commentPhoto = [None] * len(commentHTML)
		commentLikes = [None] * len(commentHTML)
		for i in range(0, len(commentHTML)):
			commentAuthor[i] = commentHTML[i].xpath('@data-author-id')[0]
			commentPhoto[i] = commentHTMl[i].xpath('@data-image-id')[0]
			commentTime[i] = commentHTML[i].xpath('time/@datetime')
			commentContent[i] = str(commentHTML[i].xpath('p'))\
				.split('<p>')[1].split('<a class="like-comment"')[0]
			commentLikes[i] = commentHTML[i].xpath(
				'p/a[@class="like-comment"]').text_content()\
				.split(u'赞同')
			if len(commentLikes[i]) == 2:
				commentLikes[i] = commentLikes[i][1]
			else:
				commentLikes[i] = ""
	print 'albumAuthorID: ' + str(albumAuthorID)
	print 'albumPostTime: ' + str(albumPostTime)
	print 'albumTitle: ' + str(albumTitle.encode('utf-8'))
	print 'albumDesc: ' + str(albumDesc.encode('utf-8'))
	print 'albumTags: ' + str(albumTags)
	print 'photoLinks: ' + str(photoLinks)
	print 'photoIDs: ' + str(photoIDs)
	print 'favoriteAuthorIDs: ' + str(favoriteAuthorIDs)
	print 'shareNum: ' + str(shareNum)
	print 'commentAuthor: ' + str(commentAuthor)
	print 'commentContent: ' + str(commentContent)
	print 'commentTime: ' + str(commentTime)
	print 'commentPhoto: ' + str(commentPhoto)
	print 'commentLikes: ' + str(commentLikes)
	raw_input("Press Enter")

# fetchAlbumLinks()
# @param: br - browser
#         currentPageHTML - html content of current page
#         tag - the tag that this program is fetching album links for
#         visited_album_links - hashmap for visited/nonvisited album links
# @return: none
# desc: give tag name, fetch albums' links of this tag into dict. 
#       Initialize values for each key (album link) to be 0, then return
def fetchAlbumLinks(br, currentPageHTML, tag,
		visited_album_links, visited_tag_lastpage):
	doc = currentPageHTML
	nextPageText = u'下一页'
	nextPageLink = doc.xpath(u'//a[text()="{0}"]'.format(nextPageText))
	if tag in visited_tag_lastpage:
		pageNum = int(visited_tag_lastpage[tag])
	else:
		pageNum = 1
	print br.geturl()
	while len(nextPageLink) != 0:
		print tag + ': page ' + str(pageNum)
		album_links = doc.xpath("//a[@class='post-cover theatre-view']/@href")
		for album_link in album_links:
			if album_link not in visited_album_links:
				visited_album_links[album_link] = 0
		visited_tag_lastpage[tag] = pageNum

		pageNum += 1
		nextPageUrl = 'http://tuchong.com/tags/' + tag + "?page=" + str(pageNum)
		page = br.open(nextPageUrl)
		doc = lxml.html.document_fromstring(page.read())
		nextPageLink = doc.xpath(u'//a[text()="{0}"]'.format(nextPageText))

# fetchByTag()
# @param: br - browser
#         tag - the tag name to be fetched from
#         visited_tags - hashmap for visited tags
#         visited_album_links - hashmap for visited links
# @return: 
def fetchByTag(br, tag, visited_tags,
	visited_album_links, visited_tag_lastpage):
	taglink = 'http://tuchong.com/tags/' + tag
	page = br.open(taglink)
	doc = lxml.html.document_fromstring(page.read())

	fetchAlbumLinks(br, doc, tag, visited_album_links, visited_tag_lastpage)
	for album_link in visited_album_links:
		if visited_album_links[album_link] == str(1):
			continue
		fetchByAlbumLink(br, album_link, visited_album_links)
		visited_album_links[album_link] = 1

# login()
# @param: br - browser
# @return: none
# desc: open mainpage, then login
def login(br):
	br.open('http://tuchong.com/')
	br.select_form(nr=0)
	br.form.set_all_readonly(False)
	br.set_handle_robots( False )
	br.set_handle_redirect(mechanize.HTTPRedirectHandler)
	br.form['user_email'] = LOGIN_USERNAME
	br.form['user_password'] = LOGIN_PASSWORD
	br.submit()

# fetchCommonTags()
# @param: br - browser
# @return: tag_dict - dict whose keys are tag names shown in the navbar
#   on the main page, and whose values are 0. This dict will be used
#   directly as the visited matrix in depth first search
# desc: fetch all tags shown in navbar into a dict, then return dict
def fetchCommonTags(br):

	# Find elements that contain those tags
	mainPage = br.open('http://tuchong.com/')
	html = mainPage.read()
	doc = lxml.html.document_fromstring(html)
	tag_uls = doc.xpath("//ul[@class='nav-tag-list clearfix']")

	# Save tags to a dict, then return the dict
	tag_dict = {}
	for tag_ul in tag_uls:
		for tag in tag_ul:
			tag = tag.xpath("a")[0].text_content().encode("utf-8")
			tag_dict[tag] = 0
	return tag_dict

if __name__=='__main__':
	br = mechanize.Browser()
	login(br) # Login

	visited_tags = {}
	visited_album_links = {}
	visited_tag_lastpage = {}

	# Initialize tag list and album list. If there exist files that contain
	#   the names and visited-or-not info, read these files into both lists.
	#   Otherwise, initialize them as the first time running this program
	visited_tags = initializeDict(br, './tags.txt', handleEmptyTagDict)
	visited_album_links = initializeDict(br, './album_links.txt',
		handleEmptyAlbumLinkDict)
	visited_tag_lastpage = initializeDict(br, './tag_pages.txt',
		handleEmptyTagPageDict)

	try:
		# Start depth first search on each tag
		for tag in visited_tags:
			if visited_tags[tag] == str(1):
				continue
			fetchByTag(br, tag, visited_tags,
				visited_album_links, visited_tag_lastpage)
			visited_tags[tag] = 1
	finally:
		finalizeDict(visited_tags, './tags.txt')
		finalizeDict(visited_album_links, './album_links.txt')
		finalizeDict(visited_tag_lastpage, './tag_pages.txt')






