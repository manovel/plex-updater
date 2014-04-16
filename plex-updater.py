import sre, urllib, urllib2, sys, BaseHTTPServer, os
from subprocess import call
import logging

#Settings:
plex_download_address = 'https://plex.tv/downloads'
last_version_installed_fn = 'last_version_installed'
logging.basicConfig(stream=sys.stdout, format='%(levelname)s: %(message)s', level=logging.DEBUG)

def retrieveWebPage(address):
        try:
                web_handle = urllib2.urlopen(address)
        except urllib2.HTTPError, e:
                error_desc = BaseHTTPServer.BaseHTTPRequestHandler.responses[e.code][0]
		logging.error(' '.join(['Cannot retrieve URL: HTTP Error Code', e.code]))
                sys.exit(1)
        except urllib2.URLError, e:
                logging.error('Cannot retrieve URL: ' + e.reason[1])
                sys.exit(1)
        except:
                logging.error('Cannot retrieve URL: unknown error')
                sys.exit(1)
        return web_handle

def loadLastVersion(filename):
	if os.path.isfile(filename) == False:
		return '0'
	else:
		f = open(filename)
		version = f.readlines()
		f.close()
		return version[0].rstrip()
		
# Find out script location:
script_root = os.path.dirname(os.path.realpath(__file__))

# Do:
last_version   = loadLastVersion(os.path.join(script_root, last_version_installed_fn))
website_handle = retrieveWebPage(plex_download_address)
website_text   = website_handle.read()

logging.debug('Parsing download page')
matches = sre.findall('<a href="(.*_i386.deb)"[^>]*>32-bit</a>', website_text)
if len(matches)>1:
	logging.error('Parsing URL: too many matches')
	sys.exit(1)

logging.debug('Parsing package file URL')
version = sre.findall('plexmediaserver_(.*)_i386.deb', matches[0])
if len(version)>1:
	logging.error('Parsing package URL: too many versions')
	sys.exit(1)

logging.debug('Comparing versions')
if last_version == version[0]:
	logging.info(version[0] + ': is already up-to-date')
	sys.exit(0)
else:
	# Remove last installer
	if last_version != '0':
		logging.debug('Removing last installer')
		try:
		    os.remove(os.path.join(script_root,'plexmediaserver_' + last_version + '_i386.deb'))
		except OSError:
		    logging.warning('Unable to remove old installer')

	# Download new installer
	logging.debug('Downloading new installer')
	# TODO: catch exceptions
	new_installer_fn = os.path.join(script_root,'plexmediaserver_' + version[0] + '_i386.deb')
	urllib.urlretrieve(matches[0], filename = new_installer_fn)

	# install
	logging.debug('Installing new version')
	# TODO: catch exceptions
	ret=call(['dpkg', '-i', new_installer_fn])

	#update latest file
	logging.debug('Updating last version file')
	# TODO: catch exceptions
	if ret==0:
		f = open(os.path.join(script_root, last_version_installed_fn),'w')
		f.write(version[0])
		f.close()

