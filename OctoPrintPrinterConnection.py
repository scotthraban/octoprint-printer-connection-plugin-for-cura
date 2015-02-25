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

import wx
import threading
import time
import cStringIO as StringIO
import traceback

from Cura.util.printerConnection import printerConnectionBase
from Cura.util.resources import getPathForImage

from plugins.OctoPrintPrinterConnection.OctoPrintHttpClient import OctoPrintHttpClient

class OctoPrintPrinterConnection(printerConnectionBase.printerConnectionBase):
	"""
	Class to connect and print files with the OctoPrint
	Auto-detects if the OctoPrint box is available and handles communication with the OctoPrint API
	"""
	def __init__(self, key, scheme, host, port, path, name, group):
		super(OctoPrintPrinterConnection, self).__init__(name)

		print "{} Connection created: {}://{}:{}{}".format(name, scheme, host, port, path)
		
		self._group = group
		
		self._key = key

		self._httpClient = OctoPrintHttpClient(scheme, host, port, path, "json")
		self._httpClient.addHeader("X-Api-Key", "YOUR_API_KEY")

		self._isAvailable = False
		self._printing = False
		self._jobFileName = None
		self._progress = 0.0;

		self._printFilename = None

		self._hotendTemperature = [None] * 4
		self._bedTemperature = None

		self._needsAuthorization = False
		
		self._errorCount = 0
		self._interruptSleep = False

		self.checkThread = threading.Thread(target=self._octoprintThread)
		self.checkThread.daemon = True
		self.checkThread.start()
		
		self.getApiKeyThread = threading.Thread(target=self._octoprintGetApiKeyThread)
		self.getApiKeyThread.daemon = True
		self.getApiKeyThread.start()


	#Load the file into memory for printing.
	def loadGCodeData(self, dataStream, filename):
		if self._printing:
			return False

		self._printFilename = filename

		response = self._httpClient.request("POST", "/api/files/local", dataStream, filename)
		if response.isOk():
			self._printFilename = filename

		self._doCallback()

		if response.isOk():
			return True
		else:
			return False

	#Start printing the previously loaded file
	def startPrint(self):
		if self._printing or not self._printFilename:
			return

		response = self._httpClient.request("POST", "/api/files/local/{}".format(self._printFilename), {"command": "select", "print": True})

		if response.isOk():
			self._printing = True
			self._interruptSleep = True
		else:
			self._printing = False
			
		self._progress = 0.0
		self._printFilename = None

	#Abort the previously loaded print file
	def cancelPrint(self):
		if not self._printing:
			return

		response = self._httpClient.request('POST', '/api/job', {'command': 'cancel'})
		if response.isOk():
			self._printing = False

	def isPrinting(self):
		return self._printing

	#Amount of progression of the current print file. 0.0 to 1.0
	def getPrintProgress(self):
		return self._progress or 0.0

	# Return if the printer with this connection type is available
	def isAvailable(self):
		return self._isAvailable

	#Are we able to send a direct coammand with sendCommand at this moment in time.
	def isAbleToSendDirectCommand(self):
		#The send command appears to be in flux, so not going to support for now
		return False

	#Directly send a command to the printer.
	def sendCommand(self, command):
		return

	# Get the connection status string. This is displayed to the user and can be used to communicate
	#  various information to the user.
	def getStatusString(self):
		if not self._isAvailable:
			return "OctoPrint is not found, or does not have a printer connected currently"
		elif self._printing:
			return "Currently printing {}".format(self._jobFileName)
		else:
			return "OctoPrint is ready to print"

	#Get the temperature of an extruder, returns None is no temperature is known for this extruder
	def getTemperature(self, extruder):
		return self._hotendTemperature[extruder]

	#Get the temperature of the heated bed, returns None is no temperature is known for the heated bed
	def getBedTemperature(self):
		return self._bedTemperature

	def _octoprintThread(self):
		while True:
			response = self._httpClient.request('GET', '/api/job')
			if response.isUnauthorized():
				self._needsAuthorization = True
				self._sleep(60)
				continue
				
			if not response.isOk():
				# No API, wait 5 seconds before looking for OctoPrint again.
				# API gave back an error
				# OctoPrint could also be offline, if we reach a high enough errorCount then assume it is gone.
				self._errorCount += 1
				if self._errorCount > 10:
					if self._isAvailable:
						self._printing = False
						self._isAvailable = False
						self._doCallback()
					self._sleep(15)
					self._group.remove(self._key)
					return
				else:
					self._sleep(3)
				continue
			if response.body['state'] == 'Closed' or response.body['state'] == "Connecting":
				# No printer connected, we do not have a printer available, but OctoPrint is there.
				# So keep trying to find a printer connected to it.
				if self._isAvailable:
					self._printing = False
					self._isAvailable = False
					self._doCallback()
				self._sleep(15)
				continue
			self._errorCount = 0

			#We got a valid status, set the OctoPrint printer as available.
			self._isAvailable = True

			self._bedTemperature = None

			self._progress = response.body["progress"]["completion"]
			if self._progress == 0:
				self._progress = None
			
			if response.body['state'] == "Printing":
				self._printing = True
				self._jobFileName = response.body["job"]["file"]["name"]
			else:
				self._printing = False
				self._jobFileName = None

			response = self._httpClient.request('GET', '/api/printer/tool')
			if response.isOk():
				self._hotendTemperature[0] = response.body['tool0']['actual']
				self._hotendTemperature[1] = response.body['tool1']['actual']
				self._hotendTemperature[2] = response.body['tool2']['actual']

			response = self._httpClient.request('GET', '/api/printer/bed')
			if response.isOk():
				self._bedTemperature = response.body['bed']['actual']

			self._doCallback()
			
			if self._printing:
				self._sleep(1)
			else:
				self._sleep(5)

	def _octoprintGetApiKeyThread(self):
		while True:
			if self._needsAuthorization:
				pass

			self._sleep(5)
		
	def _sleep(self, timeOut):
		while timeOut > 0.0:
			if not self._interruptSleep:
				time.sleep(0.1)
			timeOut -= 0.1
		self._interruptSleep = False
