import requests, json, time
from flask import Flask, render_template, g
app = Flask(__name__)

defaultPosterUrl = "https://raw.githubusercontent.com/drzoidberg33/plexpy/master/data/interfaces/default/images/poster.png"

requestUrlTemplate = "{0}:{1}/api/v2?apikey={2}&cmd=get_recently_added&count={3}&section_id={4}"
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
