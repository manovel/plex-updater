import sre, urllib, urllib2, sys, BaseHTTPServer
import os
from subprocess import call

script_root = '/usr/local/src/plex-updater'
address = 'https://plex.tv/downloads'

def retrieveWebPage(address):
        try:
                web_handle = urllib2.urlopen(address)
        except urllib2.HTTPError, e:
                error_desc = BaseHTTPServer.BaseHTTPRequestHandler.responses[e.code][0]
                #print "Cannot retrieve URL: " + str(e.code) + ": " + error_desc
                print "Cannot retrieve URL: HTTP Error Code", e.code
                sys.exit(1)
        except urllib2.URLError, e:
                print "Cannot retrieve URL: " + e.reason[1]
                sys.exit(1)
        except:
                print "Cannot retrieve URL: unknown error"
                sys.exit(1)
        return web_handle

def loadLastVersion():
	if os.path.isfile(script_root + '/last_version_installed') == False:
		return 'no_version'
	else:
		f = open(script_root + '/last_version_installed')
		version = f.readlines()
		f.close()
		return version[0].rstrip()
		

last_version = loadLastVersion()
website_handle = retrieveWebPage(address)
website_text = website_handle.read()

matches = sre.findall('<a href="(.*_i386.deb)"[^>]*>32-bit</a>', website_text)
if len(matches)>1:
	print "Error by parsing URL: too many matches"
	sys.exit(1)

version = sre.findall('plexmediaserver_(.*)_i386.deb', matches[0])
if len(version)>1:
	print "Error by parsing URL: too many versions"
	sys.exit(1)

if last_version == version[0]:
	print 'Alread up-to-date with version ' + version[0]
	sys.exit(0)
else:
	#Remove last installer
	try:
	    os.remove(script_root+'/plexmediaserver_' + last_version + '_i386.deb')
	except OSError:
	    pass
	#Download new installer
	urllib.urlretrieve(matches[0], filename= script_root+'/plexmediaserver_' + version[0] + '_i386.deb')
	#install
	ret=call(['dpkg', '-i', script_root+'/plexmediaserver_'+version[0]+'_i386.deb'])
	#update latest file
	if ret==0:
		f = open(script_root + '/last_version_installed','w')
		f.write(version[0])
		f.close()

