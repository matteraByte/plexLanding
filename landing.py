import requests, json, time
from flask import Flask, render_template, g
app = Flask(__name__)

#testtext = '{"response": {"message": null, "data": {"recently_added": [{"library_name": "", "thumb": "/library/metadata/8350/thumb/1468809683", "media_index": "", "title": "Hardcore Henry", "grandparent_thumb": "", "year": "2016", "section_id": "1", "added_at": "1468809667", "parent_rating_key": "", "parent_title": "", "grandparent_title": "", "media_type": "movie", "parent_media_index": "", "grandparent_rating_key": "", "rating_key": "8350", "parent_thumb": ""}, {"library_name": "", "thumb": "/library/metadata/8290/thumb/1468659851", "media_index": "", "title": "Frequently Asked Questions About Time Travel", "grandparent_thumb": "", "year": "2009", "section_id": "1", "added_at": "1468509079", "parent_rating_key": "", "parent_title": "", "grandparent_title": "", "media_type": "movie", "parent_media_index": "", "grandparent_rating_key": "", "rating_key": "8290", "parent_thumb": ""}, {"library_name": "", "thumb": "/library/metadata/8273/thumb/1468004988", "media_index": "", "title": "Star Trek", "grandparent_thumb": "", "year": "2009", "section_id": "1", "added_at": "1468004354", "parent_rating_key": "", "parent_title": "", "grandparent_title": "", "media_type": "movie", "parent_media_index": "", "grandparent_rating_key": "", "rating_key": "8273", "parent_thumb": ""}]}, "result": "success"}}'
#baseimgurl = 'http://matteracraft.com:8181/pms_image_proxy?img='
#endimgurl = '&width=300&height=450&fallback=poster'

defaultPosterUrl = "https://raw.githubusercontent.com/drzoidberg33/plexpy/master/data/interfaces/default/images/poster.png"

requestUrlTemplate = "{0}:{1}/api/v2?apikey={2}&cmd=get_recently_added&count={3}&section_id={4}"
pmsImageUrlTemplate = "{0}:{1}/pms_image_proxy?img={2}&width=300&height=450&fallback=poster"
notificationRequestUrlTemplate = "{0}:{1}/api/v2?apikey={2}&cmd=get_notification_log&start=0&length={3}&search={4}"
theurls = []

configFileName = 'plexLanding.config'
filename = 'cacheddata'

def assignConfig(rawConfigSettings):
	refreshImageSeconds = 0
	plexpyApiKey = ""
	plexpyPort = 0
	plexpyServerBaseUrl = ""
	requestEntryNumber = 0
	requestSectionId = 0
	notificationsLength = 0
	entryTitle = ""

	for setting in rawConfigSettings:
		configLineSplit = setting.split('=')
		configItem = configLineSplit[0].strip()
		configValue = configLineSplit[1].strip()
		if configItem == "REFRESH_IMAGE_SECONDS":
			REFRESH_IMAGE_SECONDS = configValue
		elif configItem == "PLEXPY_API_KEY":
			PLEXPY_API_KEY = configValue
		elif configItem == "PLEXPY_PORT":
			PLEXPY_PORT = configValue
		elif configItem == "PLEXPY_ROOT_URL":
			PLEXPY_ROOT_URL = configValue
		elif configItem == "NUMBER_OF_RECENT_ENTRIES":
			NUMBER_OF_RECENT_ENTRIES = configValue
		elif configItem == "RECENT_ENTRY_SECTION_ID":
			RECENT_ENTRY_SECTION_ID = configValue
		elif configItem == "NOTIFICATIONS_LENGTH":
			NOTIFICATIONS_LENGTH = configValue

	return int(REFRESH_IMAGE_SECONDS), PLEXPY_API_KEY, int(PLEXPY_PORT), PLEXPY_ROOT_URL, int(NUMBER_OF_RECENT_ENTRIES), int(RECENT_ENTRY_SECTION_ID), int(NOTIFICATIONS_LENGTH)

def populateUrls():
	del theurls[:]
	constructedRequestUrl = requestUrlTemplate.format(plexpyServerBaseUrl, plexpyPort, plexpyApiKey, requestEntryNumber, requestSectionId)
	#r = requests.get('http://matteracraft.com:8181/api/v2?apikey=3efba0ff95efeb2c80227a0d247e9ef3&cmd=get_recently_added&count=3&section_id=1')
	r = requests.get(constructedRequestUrl)
	myjson = r.json()
	entries = myjson['response']['data']['recently_added']
	for entry in entries:
		notificationsRequestUrl = notificationRequestUrlTemplate.format(plexpyServerBaseUrl, plexpyPort, plexpyApiKey, notificationsLength, entry['title'])
		r = requests.get(notificationsRequestUrl)
		myjson = r.json()
		notificationEntries = myjson['response']['data']['data']
		for notificationEntry in notificationEntries:
			if notificationEntry['poster_url'] != '':
				myurl = notificationEntry['poster_url']
				break
		#myurl = pmsImageUrlTemplate.format(plexpyServerBaseUrl, plexpyPort, entry['thumb'])
	 	#myurl = baseimgurl + entry['thumb'] + endimgurl
	 	if myurl != '' and myurl is not None:
			theurls.append(myurl)

def beforeEachLoad():
	print "beforeEachLoad"
	target = open(filename, 'r+')
	lasttime = target.readline()
	thetime = float(lasttime)
	currentTime = time.time()
	if currentTime - thetime > int(refreshImageSeconds):
		print("More time has passed...")
		populateUrls()
		target.seek(0)
		target.truncate()
		target.write(repr(currentTime))
		target.write('\n')
		print theurls
		for url in theurls:
			target.write(url)
			target.write('\n')
	else:
		print("Less time has passed...")
		del theurls[:]
		line = target.readline().rstrip('\n')
		urlIndex = 0
		while line != '':
			theurls.append(line)
			line = target.readline().rstrip('\n')
	target.close()

app.before_request(beforeEachLoad)

print("PlexLanding started...")

configFile = open(configFileName, 'r')

configFileContents = configFile.read()
print configFileContents
configFile.close()
configSettings = configFileContents.split('\n')
refreshImageSeconds, plexpyApiKey, plexpyPort, plexpyServerBaseUrl, requestEntryNumber, requestSectionId, notificationsLength = assignConfig(configSettings)


@app.route('/')
@app.route('/landing')
def landing():
    return render_template('landing.html', imageurls=theurls)