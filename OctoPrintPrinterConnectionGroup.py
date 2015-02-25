#   Copyright 2015 Scott Hraban
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

#
#   OctoPrint printer connection. Auto-detects any OctoPrint boxes on the local network.
#   This connection can then be used to send GCode to the printer.
#
#   This implementation was inspired by the Doodle3D print connection code, included
#   with the Cura application, written by David Braam, 2013
#
__copyright__ = "Copyright (C) 2015 Scott Hraban - Released under terms of the Apache License, Version 2.0"

import time
import threading
import traceback
from urlparse import urlparse

from Cura.util.printerConnection import printerConnectionBase

from plugins.OctoPrintPrinterConnection.ssdp import discover
from plugins.OctoPrintPrinterConnection.OctoPrintPrinterConnection import OctoPrintPrinterConnection
from plugins.OctoPrintPrinterConnection.OctoPrintHttpClient import OctoPrintHttpClient

class OctoPrintPrinterConnectionGroup(printerConnectionBase.printerConnectionGroup):
	"""
	The OctoPrint connection group runs a thread to poll for OctoPrint boxes.
	For each OctoPrint box it finds, it creates a OctoPrint object.
	"""

	def __init__(self):
		super(OctoPrintPrinterConnectionGroup, self).__init__("OctoPrint")
		self._connectionMap = {}
		self._ignored = []
		
		self._thread = threading.Thread(target=self._octoprintThread)
		self._thread.daemon = True
		self._thread.start()

	def getAvailableConnections(self):
		return filter(lambda c: c.isAvailable(), self._connectionMap.values())

	def remove(self, key):
		del self._connectionMap[key]

	def getIconID(self):
		return 27

	def getPriority(self):
		return 100

	def _octoprintThread(self):
		self._waitDelay = 0
		
		# self._connectionMap["hardcoded"] = OctoPrintPrinterConnection("hardcoded", "http", "192.168.8.8", 5000, "", "OctoPrint", self)
		# return
		
		while True:
			for ssdpResponse in discover("ssdp:all"):
				try:
					if ssdpResponse.usn not in self._ignored and ssdpResponse.usn not in self._connectionMap.keys():
						scheme, host, port, path = self._parseLocation(ssdpResponse.location)

						httpResponse = OctoPrintHttpClient(scheme, host, port, "", "xml").request("GET", path)
						if not httpResponse.isOk() or httpResponse.body is None:
							self._ignored.append(ssdpResponse.usn)
							continue

						manufacturer = httpResponse.body.find("{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}manufacturer")
						if manufacturer is not None:
							manufacturer = manufacturer.text
						presentationURL = httpResponse.body.find("{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}presentationURL")
						if presentationURL is not None:
							presentationURL = presentationURL.text
						
						if manufacturer and presentationURL and "octoprint" in manufacturer.lower():
							scheme, host, port, path = self._parseLocation(presentationURL)
							self._connectionMap[ssdpResponse.usn] = OctoPrintPrinterConnection(ssdpResponse.usn, scheme, host, port, path, "OctoPrint", self)
						else:
							self._ignored.append(ssdpResponse.usn)

						time.sleep(0.01)
				except:
					print "Response Error: ({}:{})".format(ssdpResponse.usn, ssdpResponse.location)
					traceback.print_exc()
					self._ignored.append(ssdpResponse.usn)


			# Delay a bit more after every request. This so we do not stress the ssdp services too much
			if self._waitDelay < 10:
				self._waitDelay += 1
			time.sleep(self._waitDelay * 60)

			
	def _parseLocation(self, location):
		parts = urlparse(location)
		
		netloc = parts.netloc.split(':')
		
		host = netloc[0]
		
		port = None
		if len(netloc) > 1:
			port = int(netloc[1])
			
		path = parts.path
		if len(path) > 0 and path[-1] == '/':
			path = path[:-1]
			
		return parts.scheme, host, port, path
